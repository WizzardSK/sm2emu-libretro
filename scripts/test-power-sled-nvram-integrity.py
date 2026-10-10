#!/usr/bin/env python3
"""Verify Power Sled native block recovery and initial images in RetroArch only.

One complete recipe, resumable runs, isolated copies of existing target-core
saves. ROM bytes are read solely to pin the native routines; no emulator other
than SM2-Emu Libretro in RetroArch acquires samples.
"""
from __future__ import annotations
import argparse
import binascii
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

from libretro_nvram_samples import find_saves
from power_sled_campaign import GAMES, ROLES, Screens, compile_sample

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROM_DIR = Path('/Volumes/MacBook External Drive/Retro/_Media/Sega - _Arcade (Model 2)/roms')


def sha(data): return hashlib.sha256(data).hexdigest()


def decode(path, game):
    data = path.read_bytes()
    if (len(data) != 64+16384+128 or data[:8] != b'SM2SRAM\0'
            or data[24:56].split(b'\0')[0].decode() != game
            or int.from_bytes(data[20:24], 'little') != binascii.crc_hqx(data[64:], 0)):
        raise RuntimeError(f'Invalid target-core SRM: {path}')
    return data[:64], data[64:64+16384], data[64+16384:]


def container(header, backup, eeprom):
    header = bytearray(header)
    header[20:24] = binascii.crc_hqx(backup+eeprom, 0).to_bytes(4, 'little')
    return bytes(header)+backup+eeprom


def selected_block(backup, base, size, default):
    blocks = [backup[base+i*256:base+i*256+size] for i in range(3)]
    for a, b in [(0,1),(0,2),(1,2)]:
        if blocks[a] == blocks[b]: return blocks[a], f'copies_{a}_{b}'
    return default, 'native_defaults'


def program_reference(rom_dir, output):
    references = {}
    for game, number, shift in [('powsled',19470,0),('powsledr',19472,16)]:
        with zipfile.ZipFile(rom_dir/f'{game}.zip') as z:
            names = [f'epr-{number}a.15',f'epr-{number+1}a.16']
            halves = [z.read(name) for name in names]
        program = bytearray(len(halves[0])*2)
        program[0::4],program[1::4] = halves[0][0::2],halves[0][1::2]
        program[2::4],program[3::4] = halves[1][0::2],halves[1][1::2]
        # Native byte comparator stops after index 27; bookkeeping after 52 bytes.
        for offset, opcode in [(0xed8d4,0x5ab58a9b),(0xed9e4,0x5995581f),
                               (0xeda0c,0x3db49fe0),(0xedce8,0x09fffc48),
                               (0xeddec,0x09fffc74)]:
            if int.from_bytes(program[offset+shift:offset+shift+4], 'little') != opcode:
                raise RuntimeError(f'Native routine signature changed: {game}/{offset:x}')
        references[game] = {
            'roms':dict(zip(names,[sha(x) for x in halves])),
            'settings_compare':hex(0xed8b0+shift),'settings_recovery':hex(0xedc20+shift),
            'settings_writer':hex(0xed930+shift),'settings_length':28,
            'settings_default':program[0xedc00+shift:0xedc1c+shift].hex(),
            'bookkeeping_compare':hex(0xed9e0+shift),'bookkeeping_recovery':hex(0xedd30+shift),
            'bookkeeping_writer':hex(0xeda60+shift),'bookkeeping_length':52,
            'bookkeeping_default':program[0xedcf0+shift:0xedd24+shift].hex(),
            'routine_sha256':sha(program[0xed880+shift:0xeddf4+shift])}
    references['powsledm'] = {**references['powsledr'],
        'program_note':'Patched Relay approximation; Main patches lie outside these routines'}
    (output/'native-routines.json').write_text(json.dumps(references,indent=2)+'\n')
    return references


def complete_plan():
    cases=[{'suffix':'unchanged','kind':'control'}]
    cases += [{'suffix':f'one-copy-{i}','kind':'majority','copies':[i]} for i in range(3)]
    cases += [{'suffix':f'two-copies-{a}-{b}','kind':'majority','copies':[a,b]} for a,b in [(0,1),(0,2),(1,2)]]
    cases += [{'suffix':'all-different','kind':'defaults'},
              {'suffix':'last-compared-byte','kind':'last_byte'},
              {'suffix':'first-excluded-byte','kind':'excluded_byte'},
              {'suffix':'initial-image-reload','kind':'reload','baseline':'all-different'}]
    return cases


def write_recipe(output, cases):
    sequence=['R3','WAIT(2.0)','L3*6','A','WAIT(1.0)','L3*3','A','WAIT(1.0)',
              'SCREENSHOT(time-values)','CLOSE']
    recipe={'macros':{},'samples':[{'suffix':c['suffix'],'sequence':sequence} for c in cases]}
    for sample in recipe['samples']: compile_sample(sample,{})
    lines=['# Complete native-integrity campaign; RetroArch target core only.','schema_version = 1','']
    for sample in recipe['samples']:
        lines += ['[[samples]]',f'suffix = {json.dumps(sample["suffix"])}',
                  f'sequence = {json.dumps(sample["sequence"])}','']
    path=output/'recipe.toml';path.write_text('\n'.join(lines))
    return path


def prepare_inputs(case, source, destination):
    for role, game in zip(ROLES,GAMES):
        saves=find_saves(source/role,game)
        if len(saves)!=1: raise RuntimeError(f'No unique baseline: {source}/{game}')
        h,b,e=decode(saves[0],game);b=bytearray(b)
        for i in range(3):
            if case['kind']=='majority' and i in case['copies']:
                b[10+i*256:12+i*256]=(80).to_bytes(2,'little')
                b[0x300+i*256]=0x5a
            elif case['kind']=='defaults':
                b[10+i*256:12+i*256]=[50,80,60][i].to_bytes(2,'little')
                b[0x300+i*256]=[0x11,0x22,0x33][i]
            elif case['kind']=='last_byte' and i==0:
                b[27+i*256]^=0x01
                b[0x333+i*256]^=0x01
            elif case['kind']=='excluded_byte':
                b[28+i*256]=i+1
                b[0x334+i*256]=i+4
            elif case['kind']=='reload':
                # Proven native ROM bookkeeping defaults; avoid captured probe time.
                b[0x300+i*256:0x334+i*256]=bytes(52)
        target=destination/role/'saves'/saves[0].name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(container(h,bytes(b),e))


def validate(case, run, inputs, refs, core_hash, screens):
    report=json.loads((run/'result.json').read_text())
    if (report['status']!='ok' or report['residual_processes']
            or report['core_sha256']!=core_hash or report['instance_sets']!=list(GAMES)
            or any(i['exit_code']!=0 or i['forced_kill'] or not i['roster_ready']
                   or not i['native_link_ready'] for i in report['instances'])):
        raise RuntimeError(f'{case["suffix"]}: lifecycle/link gate failed')
    records=[]
    for role,game in zip(ROLES,GAMES):
        before=find_saves(inputs/role,game);after=find_saves(run/role,game)
        if len(before)!=1 or len(after)!=1: raise RuntimeError('Missing unique SRM')
        _,original,ee=decode(before[0],game);_,actual,actual_ee=decode(after[0],game)
        reference=refs[game]
        settings,choice=selected_block(original,0,28,bytes.fromhex(reference['settings_default']))
        bookkeeping,book_choice=selected_block(original,0x300,52,bytes.fromhex(reference['bookkeeping_default']))
        if any(actual[i*256:i*256+28]!=settings for i in range(3)):
            raise RuntimeError(f'{game}: settings recovery differs from native code: {choice}')
        # Bookkeeping time counters advance natively; its first 28 bytes stay fixed.
        if any(actual[0x300+i*256:0x31c+i*256]!=bookkeeping[:28] for i in range(3)):
            raise RuntimeError(f'{game}: bookkeeping recovery differs from native code: {book_choice}')
        if len({actual[0x300+i*256:0x334+i*256] for i in range(3)})!=1:
            raise RuntimeError(f'{game}: bookkeeping copies differ')
        touched=set(range(0,28))|set(range(256,284))|set(range(512,540))
        touched |= {o for i in range(3) for o in range(0x300+i*256,0x334+i*256)}
        changed=[o for o,(a,b) in enumerate(zip(original,actual)) if a!=b]
        outside=[o for o in changed if o not in touched]
        if outside or ee!=actual_ee: raise RuntimeError(f'{game}: unrelated bytes changed: {outside}')
        shot=run/role/'screenshots/time-values.png'
        times=[screens.number(shot,f'checkpoint_{i}') for i in range(5)]
        expected=[int.from_bytes(settings[o:o+2],'little') for o in (10,12,14,16,18)]
        if times!=expected: raise RuntimeError(f'{game}: visible time mismatch: {times}/{expected}')
        if (run/role/'samples'/f'{game}.nv').read_bytes()!=actual:
            raise RuntimeError('Native extraction differs from frontend SRM')
        records.append({'set':game,'settings_choice':choice,'bookkeeping_choice':book_choice,
            'time_values':times,'settings_hex':settings.hex(),'all_copies_concordant':True,
            'unrelated_bytes_preserved':True,'eeprom_preserved':True,
            'backup':str(run/role/'samples'/f'{game}.nv'),'backup_sha256':sha(actual),
            'srm':str(after[0]),'srm_sha256':sha(after[0].read_bytes()),
            'screenshot':str(shot),'screenshot_sha256':sha(shot.read_bytes()),
            'bookkeeping_last_byte':actual[0x333],
            'excluded_bytes':[actual[28+i*256] for i in range(3)],
            'bookkeeping_excluded_bytes':[actual[0x334+i*256] for i in range(3)]})
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rom-dir',type=Path,default=DEFAULT_ROM_DIR)
    p.add_argument('--core',type=Path,default=ROOT/'build-libretro-gpu/libretro/sm2_libretro.dylib')
    p.add_argument('--baseline',type=Path)
    p.add_argument('--dry-run',action='store_true')
    args=p.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    old=json.loads((ROOT/'build-libretro-gpu/validation/power-sled-phase2-20261009/campaign.json').read_text())
    baseline=(args.baseline or Path(old['samples']['ride-black-reload']['run'])).resolve()
    refs=program_reference(args.rom_dir,out)
    if any(bytes.fromhex(r['bookkeeping_default'])!=bytes(52) for r in refs.values()):
        raise RuntimeError('Native bookkeeping defaults changed')
    cases=complete_plan();recipe=write_recipe(out,cases)
    (out/'plan.json').write_text(json.dumps(cases,indent=2)+'\n')
    core_hash=sha(args.core.read_bytes());journal_path=out/'campaign.json'
    journal=json.loads(journal_path.read_text()) if journal_path.exists() else {
        'backend':'SM2-Emu Libretro In RetroArch Only','stages':{}}
    if journal.get('core_sha256',core_hash)!=core_hash:raise RuntimeError('Core changed; select new output')
    journal.update(core_sha256=core_hash,recipe_sha256=sha(recipe.read_bytes()),status='running',planned_stages=len(cases))
    def save():journal_path.write_text(json.dumps(journal,indent=2)+'\n')
    save();screens=Screens();paths={}
    try:
        for index,case in enumerate(cases,1):
            name=case['suffix'];source=paths.get(case.get('baseline'),baseline)
            prior=journal['stages'].get(name)
            if prior and prior['status']=='validated' and case['kind']=='reload':
                normalized=all(decode(find_saves(Path(prior['inputs'])/r,g)[0],g)[1][0x300+i*256:0x334+i*256]==bytes(52)
                    for r,g in zip(ROLES,GAMES) for i in range(3))
                if not normalized:
                    journal.setdefault('superseded_initial_image_probes',[]).append(prior)
                    prior=None
            if prior and prior['status']=='validated':
                run=Path(prior['run']);inputs=Path(prior['inputs'])
            else:
                attempts=list(out.glob(f'{name}-attempt-*'))
                attempt=max([int(x.name.rsplit('-',1)[1]) for x in attempts if x.is_dir()],default=0)+1
                run=out/f'{name}-attempt-{attempt:02d}';inputs=out/f'{name}-inputs-{attempt:02d}'
                prepare_inputs(case,source,inputs)
                cmd=[sys.executable,str(ROOT/'scripts/test-retroarch-netpacket.py'),
                    '--retroarch',str(Path.home()/'Retro/Apps/RetroArch/Nightly/RetroArch (ARM).app/Contents/MacOS/RetroArch'),
                    '--core',str(args.core),'--rom',str(args.rom_dir/'powsledm.zip'),
                    '--relay-rom',str(args.rom_dir/'powsledr.zip'),'--slave-rom',str(args.rom_dir/'powsled.zip'),
                    '--system-assets',str(ROOT/'build-libretro-gpu/libretro/system/sm2-emu'),
                    '--set-name','powsledm','--cabinets','3','--operator-recipe',str(recipe),
                    '--sample',name,'--baseline-run',str(inputs),'--output',str(run),
                    '--startup-wait','5','--settle','18','--port','55435']
                (out/f'{name}-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
                if args.dry_run:
                    print(f'[{index}/{len(cases)}] Planned {name}',flush=True)
                    # Reload planning only: source remains the original valid baseline.
                    paths[name]=baseline;continue
                journal['stages'][name]={'status':'acquiring','run':str(run),'inputs':str(inputs)};save()
                print(f'[{index}/{len(cases)}] Acquiring {name}',flush=True)
                with (out/f'{name}-attempt-{attempt:02d}.log').open('w') as log:
                    subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
            records=validate(case,run,inputs,refs,core_hash,screens)
            (run/'validation.json').write_text(json.dumps({'status':'passed','records':records},indent=2)+'\n')
            journal['stages'][name]={'status':'validated','run':str(run),'inputs':str(inputs),'records':records};save()
            paths[name]=run;print(f'[{index}/{len(cases)}] Validated {name}',flush=True)
        if args.dry_run:journal['status']='planned';save();return
        candidates=journal['stages']['initial-image-reload']['records']
        for record in candidates:
            game=record['set'];role=ROLES[GAMES.index(game)]
            initial_srm=find_saves(Path(journal['stages']['initial-image-reload']['inputs'])/role,game)[0]
            h,b,e=decode(initial_srm,game)
            reference=refs[game]
            if b[:28]!=bytes.fromhex(reference['settings_default']):raise RuntimeError('Candidate lost native defaults')
            if any(b[0x300+i*256:0x334+i*256]!=bytes.fromhex(reference['bookkeeping_default']) for i in range(3)):
                raise RuntimeError('Initial image must use native bookkeeping defaults')
            folder=out/'initial-images';folder.mkdir(exist_ok=True)
            target=folder/f'{game}.bin';target.write_bytes(b+e)
            record['initial_payload']=str(target);record['initial_payload_sha256']=sha(b+e)
            record['initial_image_source']=str(initial_srm)
            record['initial_image_note']='Exact complete per-set input reloaded natively; bookkeeping reset to native ROM defaults'
        journal['status']='native_integrity_and_per_set_initial_images_validated';save()
        (out/'coverage.json').write_text(json.dumps({**journal,
            'native_integrity':{'settings':{'base':0,'stride':256,'copies':3,'length':28},
                'bookkeeping':{'base':768,'stride':256,'copies':3,'length':52},
                'rule':'First Equal Whole-Block Pair; No Matching Pair Uses ROM Defaults',
                'checksum':'No checksum in these native comparison/recovery routines'},
            'initial_images':candidates,'limits':['No parent-template reuse claim','No gameplay claim',
                'Country/Relay interpretation and ID attribution remain deferred',
                'No Core Option, automatic policy or calibration preset implemented']},indent=2)+'\n')
        print(f'Validated {len(cases)} stages / {3*len(cases)} program records; three independent initial images',flush=True)
    except Exception as error:
        journal.update(status='failed',error=str(error));save();raise


if __name__=='__main__':main()
