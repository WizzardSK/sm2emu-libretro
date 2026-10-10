#!/usr/bin/env python3
"""Complete, resumable Power Sled acquisition through the existing linked runner.

Game-specific planning/validation stays outside the generic process lifecycle.
Reference PNGs are read only; only RetroArch may acquire samples.
"""
from __future__ import annotations

import hashlib
import binascii
import json
import re
from pathlib import Path
import subprocess
import sys
import time

from libretro_nvram_samples import Action, expand_actions, validate_close, action_label as basic_action_label, find_saves

ROOT = Path(__file__).resolve().parent.parent
GAMES = ('powsledm', 'powsledr', 'powsled')
ROLES = ('host', 'client1', 'client2')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def action_label(action):
    return f'RIDE_CYCLE({action.value})' if action.kind=='ride_cycle' else basic_action_label(action)


def compile_sample(sample, macros):
    steps = sample.get('steps', [{'sets': list(GAMES), 'sequence': sample.get('sequence', [])}])
    actions, targets = [], []
    for step in steps:
        selected = step.get('sets', list(GAMES))
        if not selected or len(set(selected)) != len(selected) or set(selected) - set(GAMES):
            raise RuntimeError('Unknown/duplicate program in recipe step')
        expanded = []
        for token in step['sequence']:
            cycle = re.fullmatch(r'RIDE_CYCLE\(([12])\)', token)
            if cycle:
                if len(selected)!=1 or selected[0]=='powsledr':
                    raise RuntimeError('A visible Ride cycle requires one Main or Slave program')
                expanded.append(Action('ride_cycle',cycle[1]))
            else: expanded.extend(expand_actions([token], macros))
        actions.extend(expanded)
        targets.extend([selected] * len(expanded))
    validate_close(actions)
    if any(a.kind not in {'button', 'wait', 'screenshot', 'close', 'ride_cycle'} for a in actions):
        raise RuntimeError('Linked campaign supports buttons, waits, screenshots and final CLOSE')
    return actions, targets


def preflight(campaign):
    samples = campaign.get('samples', [])
    if not samples:
        raise RuntimeError('Empty campaign')
    seen = set()
    for sample in samples:
        name = sample['suffix']
        if not name or Path(name).name != name or name in seen:
            raise RuntimeError('Unsafe or duplicate sample suffix')
        if sample.get('baseline') and sample['baseline'] not in seen:
            raise RuntimeError(f'{name}: baseline must precede sample')
        compile_sample(sample, campaign.get('macros', {}))
        seen.add(name)
    for source in campaign.get('inventory', []):
        path = ROOT / source['path']
        text = path.read_text()
        if 'status: service_menu_documented' not in text:
            raise RuntimeError(f'Phase 1 is incomplete: {path}')
        # Pin the completed menu topology, allowing later evidence reconciliation.
        menu = json.JSONDecoder().raw_decode(text.split('menus:', 1)[1].lstrip())[0]
        if digest(json.dumps(menu, sort_keys=True).encode()) != source['menu_sha256']:
            raise RuntimeError(f'Inventory changed; regenerate complete recipe: {path}')
    return samples


class Screens:
    def __init__(self):
        from PIL import Image
        self.Image = Image
        refs = ROOT / 'build-libretro-gpu/validation/power-sled-settings-20261008/mame-time0-range/1-powsledm'
        self.templates = {self.glyph(refs / f'screen-{n-2:04d}.png', 296, 68): str(n % 10)
                          for n in range(5, 15)}
        if len(self.templates) != 10:
            raise RuntimeError('Incomplete documented font reference')
        self.blank = bytes(112)
        self.inventory = ROOT / 'build-libretro-gpu/validation/power-sled-phase1-20261008/initialized-menu'

    def image(self, path):
        with self.Image.open(path) as source:
            im = source.convert('RGB')
        if im.size == (1024, 768):
            im = im.resize((496, 384), self.Image.Resampling.NEAREST)
        if im.size != (496, 384):
            raise RuntimeError(f'Unexpected screenshot dimensions: {path}: {im.size}')
        return im

    def glyph(self, path, x, y):
        im = self.image(path)
        return bytes(int(r > 180 and g > 180) for r, g, b in im.crop((x, y, x+8, y+14)).getdata())

    def number(self, path, setting):
        points = ([(232, 172), (240, 172), (256, 172)] if setting == 'motion'
                  else [(x, 68+16*int(setting.rsplit('_', 1)[1])) for x in (264, 272, 280, 288, 296)])
        values = []
        for x, y in points:
            glyph = self.glyph(path, x, y)
            if glyph == self.blank:
                values.append(' ')
            elif glyph in self.templates:
                values.append(self.templates[glyph])
            else:
                raise RuntimeError(f'Unrecognized visible digit: {path}: {(x,y)}')
        return int(''.join(values))

    def ride(self, path, game):
        if game=='powsledr': raise RuntimeError('Relay role label cannot identify its stored byte')
        for value in (0,1,2):
            try: self.discrete(path,'ride_id',value,game);return value
            except RuntimeError: pass
        raise RuntimeError(f'Unrecognized visible Ride color: {path}')

    def discrete(self, path, setting, value, game):
        if setting == 'country':
            ref = self.inventory / '1-powsledm/screen-0013.png'
        elif value == 255 and game != 'powsledr':
            ref = self.inventory / '1-powsledm/screen-0003.png'
        elif game == 'powsledr':
            ref = self.inventory / '2-powsledr/screen-0003.png'
        else:
            ref = self.inventory / f'1-powsledm/screen-{4+value:04d}.png'
        box = (160, 140, 360, 156)
        if self.image(path).crop(box).tobytes() != self.image(ref).crop(box).tobytes():
            raise RuntimeError(f'Visible {setting} mismatch: {game}: {path}')


def validate_sample(sample, run, core_hash, screens, baseline=None):
    report = json.loads((run / 'result.json').read_text())
    if (report['status'] != 'ok' or report['residual_processes']
            or report['core_sha256'] != core_hash
            or report['instance_sets'] != list(GAMES)
            or len(report['operator_saves']) != 3):
        raise RuntimeError(f'{sample["suffix"]}: linked lifecycle/core/SRM gate failed')
    if any(i['exit_code'] != 0 or i['forced_kill'] or not i['roster_ready']
           or not i['native_link_ready'] for i in report['instances']):
        raise RuntimeError('Unclean exit or native link failure')
    records = []
    setting = sample['setting']
    for index, (role, game) in enumerate(zip(ROLES, GAMES)):
        nv = run / role / 'samples' / f'{game}.nv'
        blob = nv.read_bytes()
        containers = find_saves(run / role, game)
        if len(containers) != 1:
            raise RuntimeError(f'{game}: missing unique frontend SRM')
        container = containers[0].read_bytes()
        eeprom = (run / role / 'samples' / f'{game}.eeprom').read_bytes()
        if (len(container) != 64+16384+128 or container[:8] != b'SM2SRAM\0'
                or container[24:56].split(b'\0')[0].decode() != game
                or int.from_bytes(container[20:24], 'little') != binascii.crc_hqx(container[64:], 0)
                or container[64:] != blob+eeprom):
            raise RuntimeError(f'{game}: invalid SRM identity/CRC or extraction mismatch')
        offset = sample['offset']
        size = sample.get('width', 2)
        copies = [int.from_bytes(blob[offset+s:offset+s+size], 'little') for s in (0, 256, 512)]
        if len(blob) != 16384 or len(set(copies)) != 1:
            raise RuntimeError(f'{game}: invalid native image or disagreeing copies: {copies}')
        raw = sample.get('expected', [None]*3)[index]
        if raw=='observed': raw = None
        previous = None
        if baseline:
            before = (baseline / role / 'samples' / f'{game}.nv').read_bytes()
            previous = int.from_bytes(before[offset:offset+size], 'little')
        if sample.get('toggle'):
            raw = 1-previous
        if raw is None and sample.get('reload_only') and previous is not None:
            raw = previous
        if raw is None:
            if copies[0] not in sample.get('allowed', [0, 1]):
                raise RuntimeError(f'{game}: unexpected stored selector state {copies[0]}')
            raw = copies[0]
        if copies != [raw]*3:
            raise RuntimeError(f'{game}: expected {raw}, native copies {copies}')
        shot = run / role / 'screenshots' / f'{sample["screenshot"]}.png'
        if setting in {'motion'} or setting.startswith('checkpoint_'):
            visible = screens.number(shot, setting)
            if visible != raw:
                raise RuntimeError(f'{game}: visible {visible}, expected {raw}: {shot}')
        else:
            screens.discrete(shot, setting, raw, game)
        # Verify every named intermediate color, including closing cycles.
        # The Relay always reports its program role on these value lines.
        cycle_screens = []
        if setting == 'ride_id':
            colors = {'red':1, 'black':2, 'silver':0}
            steps = sample.get('steps', [{'sets':list(GAMES), 'sequence':sample.get('sequence',[])}])
            for step in steps:
                if game not in step.get('sets', list(GAMES)): continue
                for action in step['sequence']:
                    match = re.fullmatch(r'SCREENSHOT\((?:initial|cycle)-(red|black|silver)\)', action)
                    cycle = re.fullmatch(r'RIDE_CYCLE\(([12])\)', action)
                    if cycle:
                        start = run/role/'screenshots/ride-cycle-start.png'
                        target = int(cycle[1])
                        if screens.ride(start,game)!=target:
                            raise RuntimeError('Ride cycle did not start at its committed color')
                        sequence = [target]
                        pictures = sorted((run/role/'screenshots').glob('ride-cycle-[0-9][0-9].png'))
                        if not 2<=len(pictures)<=3: raise RuntimeError('Incomplete bounded Ride cycle')
                        for picture in pictures:
                            color = screens.ride(picture,game)
                            if color==sequence[-1]: raise RuntimeError('Repeated unclosed Ride color')
                            sequence.append(color)
                            cycle_screens.append({'label':picture.stem,'visible_id':color,
                                'screenshot':str(picture),'screenshot_sha256':digest(picture.read_bytes())})
                        if sequence[-1]!=target or len(set(sequence[:-1]))!=len(sequence)-1:
                            raise RuntimeError('Ride cycle did not close after every distinct value')
                    if not match: continue
                    label = action[len('SCREENSHOT('):-1]
                    color = 0 if game == 'powsledr' else colors[match[1]]
                    picture = run / role / 'screenshots' / f'{label}.png'
                    screens.discrete(picture, setting, color, game)
                    cycle_screens.append({'label':label, 'visible_id':256 if game=='powsledr' else color,
                        'screenshot':str(picture),
                        'screenshot_sha256':digest(picture.read_bytes())})
        reload_shot = None
        if sample.get('before_screenshot') and baseline:
            reload_shot = run / role / 'screenshots' / f'{sample["before_screenshot"]}.png'
            if setting == 'motion' or setting.startswith('checkpoint_'):
                prior = screens.number(reload_shot, setting)
                if prior != previous:
                    raise RuntimeError(f'{game}: fresh reload {prior}, saved {previous}')
            elif not (sample.get('bootstrap_reload') and previous == 255):
                screens.discrete(reload_shot, setting, previous, game)
            else:
                reload_shot = None  # Uninitialized 255 is not a persistent preset.
        differences = [i for i,(a,b) in enumerate(zip(before,blob)) if a!=b] if baseline else []
        field_bytes = {offset+s+j for s in (0,256,512) for j in range(size)}
        records.append({'set': game, 'raw': raw, 'copies': copies,
                        'changed_bytes': differences,
                        'changes_outside_field': [i for i in differences if i not in field_bytes],
                        'backup': str(nv), 'backup_sha256': digest(blob),
                        'screenshot': str(shot), 'screenshot_sha256': digest(shot.read_bytes()),
                        'cycle_screens':cycle_screens,
                        'fresh_reload_of_baseline': bool(reload_shot or sample.get('reload_only'))})
    return records


def run_campaign(args, campaign, recipe):
    samples = preflight(campaign)
    screens = Screens()  # Dependencies/references validated before any launch.
    if not args.output:
        raise RuntimeError('Complete campaign requires persistent --output for resume')
    output = args.output.expanduser().resolve()
    core_hash = digest(args.core.expanduser().resolve(strict=True).read_bytes())
    output.mkdir(parents=True, exist_ok=True)
    journal_path = output / 'campaign.json'
    journal = json.loads(journal_path.read_text()) if journal_path.exists() else {
        'backend': 'SM2-Emu Libretro In RetroArch Only', 'samples': {}, 'created': time.time()}
    if journal.get('core_sha256', core_hash) != core_hash:
        raise RuntimeError('Core changed; use a new campaign output directory')
    if journal.get('failure'):
        journal.setdefault('failure_history', []).append({'error':journal.pop('failure'),
            'time':journal.get('updated'), 'stages':{k:v.get('run') for k,v in journal['samples'].items()
             if v.get('status')!='validated'}})
    superseded = {key:row for key,row in journal['samples'].items()
                  if key not in {sample['suffix'] for sample in samples}}
    if superseded:
        journal.setdefault('superseded_stages', []).append({'time':time.time(), 'samples':superseded})
        for key in superseded: del journal['samples'][key]
    journal.update(core_sha256=core_hash, recipe=str(recipe), recipe_sha256=digest(recipe.read_bytes()),
                   planned_samples=len(samples), status='running')
    def write():
        journal['updated'] = time.time()
        temp = output / 'campaign.json.tmp'
        temp.write_text(json.dumps(journal, indent=2)+'\n')
        temp.replace(journal_path)
    write()
    # Retain exact invocation and a complete expanded plan before acquisition.
    (output / 'plan.json').write_text(json.dumps([
        {**sample, 'expanded': [{'targets': t, 'action': action_label(a)} for a, t in
          zip(*compile_sample(sample, campaign.get('macros', {})))]} for sample in samples], indent=2)+'\n')
    paths = {}
    try:
        for position, sample in enumerate(samples, 1):
            name = sample['suffix']
            baseline = paths.get(sample.get('baseline'))
            signature = digest(json.dumps({'sample': sample, 'macros': campaign.get('macros', {}),
                'baseline_hashes': [digest((baseline/r/'samples'/f'{g}.nv').read_bytes())
                                    for r,g in zip(ROLES,GAMES)] if baseline else []}, sort_keys=True).encode())
            cached = journal['samples'].get(name)
            run = Path(cached['run']) if cached and cached.get('signature') == signature and cached.get('status') == 'validated' else None
            if run is None and sample.get('reuse'):
                run = ROOT / sample['reuse']
            if run is None and not args.dry_run:
                attempts = [p for p in output.glob(f'{name}-attempt-*') if p.is_dir()]
                attempt = max([int(p.name.rsplit('-',1)[1]) for p in attempts],default=0)+1
                run = output / f'{name}-attempt-{attempt:02d}'
                command = [sys.executable, str(ROOT/'scripts/test-retroarch-netpacket.py'),
                    '--retroarch', str(args.retroarch), '--core', str(args.core), '--rom', str(args.rom),
                    '--relay-rom', str(args.relay_rom), '--slave-rom', str(args.slave_rom),
                    '--base-config', str(args.base_config), '--system-assets', str(args.system_assets),
                    '--set-name', 'powsledm', '--cabinets', '3', '--operator-recipe', str(recipe),
                    '--sample', name, '--output', str(run), '--settle', str(args.settle),
                    '--startup-wait', str(args.startup_wait), '--port', str(args.port)]
                if baseline:
                    command += ['--baseline-run', str(baseline)]
                journal['samples'][name] = {'status': 'acquiring', 'run': str(run), 'signature': signature}
                write()
                print(f'[{position}/{len(samples)}] Acquiring {name}', flush=True)
                with (output / f'{name}-attempt-{attempt:02d}.log').open('w') as log:
                    subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
            if args.dry_run and run is None:
                print(f'[{position}/{len(samples)}] Planned {name}', flush=True)
                # No acquired baseline exists for future samples in a dry run.
                paths[name] = None
                continue
            try:
                records = validate_sample(sample, run, core_hash, screens, baseline)
            except Exception as error:
                (run/'validation.json').write_text(json.dumps({'status':'failed',
                    'sample':sample, 'error':str(error)},indent=2)+'\n')
                journal['samples'][name].update(status='validation_failed',error=str(error))
                raise
            (run/'validation.json').write_text(json.dumps({'status':'passed',
                'sample':sample, 'records':records},indent=2)+'\n')
            journal['samples'][name] = {'status': 'validated', 'run': str(run),
                'signature': signature, 'records': records, 'reused': bool(sample.get('reuse'))}
            if sample.get('baseline') and all(r['fresh_reload_of_baseline'] for r in records):
                journal['samples'][sample['baseline']]['fresh_reload_verified_by'] = name
            paths[name] = run
            write()
            print(f'[{position}/{len(samples)}] Validated {name}', flush=True)
        journal['status'] = 'planned' if args.dry_run else 'acquisition_validated'
    except (Exception, KeyboardInterrupt) as error:
        journal['status'] = 'failed'
        journal['failure'] = f'{type(error).__name__}: {error}'
        write()
        raise
    journal.pop('failure', None)
    write()
    print(f'Campaign {journal["status"]}: {journal_path}', flush=True)
    return 0


def review_campaign(output):
    """Recheck complete acquired evidence without launching any emulator."""
    import tomllib
    journal = json.loads((output/'campaign.json').read_text())
    if journal['status'] != 'acquisition_validated':
        raise RuntimeError('Campaign acquisition is not complete')
    recipe = Path(journal['recipe'])
    with recipe.open('rb') as stream:
        campaign = tomllib.load(stream)
    samples = preflight(campaign)
    screens = Screens()
    records = []
    for sample in samples:
        row = journal['samples'][sample['suffix']]
        if row['status'] != 'validated':
            raise RuntimeError('Unvalidated campaign stage')
        baseline = Path(journal['samples'][sample['baseline']]['run']) if sample.get('baseline') else None
        checked = validate_sample(sample, Path(row['run']), journal['core_sha256'], screens, baseline)
        for old, new in zip(row['records'], checked):
            if any(old[k] != new[k] for k in ('set','raw','backup_sha256','screenshot_sha256')):
                raise RuntimeError('Acquired evidence changed after validation')
        if not sample.get('reload_only') and not sample.get('setup_only') and not row.get('fresh_reload_verified_by'):
            raise RuntimeError(f'{sample["suffix"]}: native edit has no fresh reload proof')
        records.extend({'stage':sample['suffix'], 'setting':sample['setting'],
                        'fresh_reload_verified_by': row.get('fresh_reload_verified_by'),
                        'setup_only':bool(sample.get('setup_only')), **r} for r in checked)
    summary = {'status':'acquisition_and_native_reload_validated',
        'backend':journal['backend'],'core_sha256':journal['core_sha256'],
        'scope':'Operator Field Mapping; Further ID Assignment Logic Deferred By User',
        'stages':len(samples),'records':records,
        'settings':['country','ride_id']+[f'checkpoint_{i}' for i in range(5)]+['motion'],
        'calibration':'Listed Only; Excluded From Acquisition',
        'country':'Export Label Only; Stored 0/1 Semantics Unresolved',
        'relay':{'visible_label':'Relay','reported_role_id':256,
                 'observed_stored_bytes':sorted({r['raw'] for r in records
                    if r['set']=='powsledr' and r['setting']=='ride_id'}),
                 'meaning':'Unresolved; Not Additional Visible Color Choices'},
        'pending':['General Native Integrity Algorithm','Complete Initial Image Suitability',
                   'Country Semantics','Conditional Ride ID Assignment Logic','Core Option Review','Automatic Policies','Linked Gameplay']}
    (output/'coverage.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Review completed linked RetroArch acquisition; no emulator launch')
    parser.add_argument('output',type=Path)
    result = review_campaign(parser.parse_args().output.resolve())
    print(f'Power Sled: {result["stages"]} stages / {len(result["records"])} independent program records validated')
