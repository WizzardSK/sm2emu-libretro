#!/usr/bin/env python3
"""Review automatic cabinet presets through the established RetroArch runner.

Retains each attempt separately; verifies saved native fields, board handshakes
and process cleanup. This is network evidence, not synchronized gameplay proof.
"""
import argparse
import binascii
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from PIL import Image
from test_retroarch_network_data import CASES, expected_fields, patch_catalog

ROOT = Path(__file__).resolve().parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review(run, case, catalog):
    result = json.loads((run/'result.json').read_text())
    if result['status'] != 'ok' or result['residual_processes']:
        raise RuntimeError('Runner lifecycle/roster failed')
    records = []
    for index, instance in enumerate(result['instances']):
        if instance['exit_code'] != 0 or instance['forced_kill']:
            raise RuntimeError('Instance did not exit cleanly')
        role = instance['role']
        game = result['instance_sets'][index]
        saves = list((run/role/'saves').glob('*.srm'))
        if len(saves) != 1:
            raise RuntimeError(f'{role}: no unique SRAM')
        data = saves[0].read_bytes()
        if (data[:8] != b'SM2SRAM\0' or data[24:56].split(b'\0')[0].decode() != game
                or binascii.crc_hqx(data[64:],0) != int.from_bytes(data[20:24],'little')):
            raise RuntimeError(f'{role}: invalid SRAM identity/CRC')
        size = int.from_bytes(data[12:16],'little')
        memory = {'BackupRam':data[64:64+size],'Eeprom':data[64+size:]}
        fields = expected_fields(case, index)
        observed = []
        for (native_game, suffix), value in fields.items():
            patches, desired = catalog[native_game,suffix,value]
            for (offset,mask,kind), wanted in zip(patches,desired):
                actual = memory[kind][offset] & mask
                if actual != wanted & mask:
                    raise RuntimeError(f'{role}: {suffix}/{value} at {kind}:{offset:x}: {actual:x} != {wanted & mask:x}')
            observed.append({'catalog':native_game,'field':suffix,'value':value,'patch_count':len(patches)})
        # Retain successful native-field proof even when later board
        # qualification fails. Preset persistence and playable linking differ.
        (run/role/'network-fields-review.json').write_text(json.dumps({
            'set':game,'role':role,'core_sha256':result['core_sha256'],
            'sram_crc_verified':True,'fields':observed,
            'srm_sha256':digest(saves[0])},indent=2)+'\n')
        log = Path(instance['log']).read_text(errors='replace')
        # Closing a peer legitimately drops the remaining boards' link status.
        # Review the established session before the runner's ordered cleanup.
        log = log.split('Cabinet disconnected',1)[0]
        states = [tuple(map(int,m)) for m in re.findall(
            r'Native board \S+: enabled=(\d+) alive=(\d+) id=(\d+) count=(\d+)',log)]
        if not states or states[-1][0:2] != (1,1):
            raise RuntimeError(f'{role}: native board not linked: {states[-1:]!r}')
        if game in {'manxtt', 'manxttc', 'manxttdx'}:
            if not 1 <= states[-1][2] <= states[-1][3] == case['count']:
                raise RuntimeError(f'{role}: Manx TT requires a counted native ID in 1..count')
            first_alive = next(i for i, state in enumerate(states) if state[:2] == (1,1))
            if any(state[:2] != (1,1) for state in states[first_alive:]):
                raise RuntimeError(f'{role}: Manx TT board restarted after establishment')
        if any(marker in log for marker in ['queue overflow','Queue overflow','incompatible','Failed to connect to host']):
            raise RuntimeError(f'{role}: network error in log')
        pictures=list((run/role/'screenshots').glob('*.png'))
        if not pictures:raise RuntimeError(f'{role}: no screenshot evidence')
        for picture in pictures:
            with Image.open(picture) as image:image.verify()
        shots = [{'path':str(p),'sha256':digest(p)} for p in pictures]
        records.append({'set':game,'role':role,'fields':observed,'native_state':states[-1],
                        'srm_sha256':digest(saves[0]),'screenshots':shots})
    if len({r['native_state'][3] for r in records}) != 1:
        raise RuntimeError('Native boards disagree on link count')
    return {'status':'preset_and_native_link_verified','result':str(run/'result.json'),
            'result_sha256':digest(run/'result.json'),'programs':records}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--case',action='append',choices=[c['name'] for c in CASES])
    p.add_argument('--core',type=Path,default=Path.home()/'Library/Application Support/RetroArch/cores/sm2_libretro.dylib')
    p.add_argument('--retroarch',type=Path,default=Path.home()/'Retro/Apps/RetroArch/Nightly/RetroArch (ARM).app/Contents/MacOS/RetroArch')
    p.add_argument('--rom-dir',type=Path,default=Path('/Volumes/MacBook External Drive/Retro/_Media/Sega - _Arcade (Model 2)/roms'))
    p.add_argument('--settle',type=float,default=18)
    args = p.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    identity = {'core_sha256':digest(args.core),'assets_sha256':digest(ROOT/'build-libretro-gpu/libretro/system/sm2-emu/games.xml')}
    coverage = {'identity':identity,'cases':{}}
    if (out/'coverage.json').exists():
        coverage=json.loads((out/'coverage.json').read_text())
        if coverage['identity'] != identity: raise RuntimeError('Core/assets changed; choose a new output directory')
    catalog=patch_catalog(ROOT/'src/libretro/nvram_settings_data.inc')
    selected=[c for c in CASES if not args.case or c['name'] in args.case]
    for case in selected:
        for index in range(case['count']):
            for (game,suffix),value in expected_fields(case,index).items():
                if (game,suffix,value) not in catalog:
                    raise RuntimeError(f'Unresolved native patch metadata: {game}/{suffix}/{value}')
    failures=[]
    for case in selected:
        name=case['name'];prior=coverage['cases'].get(name)
        if not prior:
            attempts=sorted(out.glob(name+'-attempt-*/result.json'))
            if attempts:
                prior={'run':str(attempts[-1].parent),'case':case}
                coverage['cases'][name]=prior
        if prior and (Path(prior['run'])/'result.json').exists():
            try:
                prior.update(review(Path(prior['run']),case,catalog))
                prior.pop('error',None)
                (out/'coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
                print(name+': retained verified run',flush=True);continue
            except RuntimeError:
                pass
        attempt=len(list(out.glob(name+'-attempt-*')))+1
        run=out/f'{name}-attempt-{attempt:02d}'
        cmd=[sys.executable,str(ROOT/'scripts/test-retroarch-netpacket.py'),
             '--retroarch',str(args.retroarch),'--core',str(args.core),
             '--rom',str(args.rom_dir/(case['game']+'.zip')),'--set-name',case['game'],
             '--system-assets',str(ROOT/'build-libretro-gpu/libretro/system/sm2-emu'),
             '--cabinets',str(case['count']),'--automatic-network',
             '--capture-screenshots','--settle',str(args.settle),'--output',str(run)]
        if case.get('relay'):cmd+=['--include-relay']
        if case['game']=='von' and case['count']==3:cmd+=['--relay-rom',str(args.rom_dir/'vonr.zip')]
        (out/(run.name+'-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
        print(name+': running',flush=True)
        record={'status':'failed','run':str(run),'case':case}
        try:
            with (out/(run.name+'.log')).open('w') as log:
                # The child owns bounded stages and finally-based PID cleanup.
                # Killing it with an outer timeout would bypass that cleanup.
                subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
            record.update(review(run,case,catalog))
        except (OSError,RuntimeError,subprocess.SubprocessError) as error:
            record['error']=str(error);failures.append(name)
        coverage['cases'][name]=record
        (out/'coverage.json').write_text(json.dumps(coverage,indent=2)+'\n')
        print(name+': '+record['status']+(' '+record.get('error','')),flush=True)
    if failures:raise SystemExit('Cases needing diagnosis: '+', '.join(failures))


if __name__=='__main__':main()
