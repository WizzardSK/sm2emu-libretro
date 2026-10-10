#!/usr/bin/env python3
"""Verify Power Sled Core Options, initial seeding and save precedence in RetroArch.

Reuses the existing three-program lifecycle and documented operator navigation.
One complete five-stage recipe; records are retained outside tracked source.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from power_sled_campaign import GAMES, ROLES, Screens
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('power_integrity', ROOT/'scripts/test-power-sled-nvram-integrity.py')
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--core', type=Path, default=ROOT/'build-libretro-gpu/libretro/sm2_libretro.dylib')
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    sequence = ['R3','WAIT(2.0)','L3*6','A','WAIT(1.0)',
        'L3*3','A','WAIT(1.0)','SCREENSHOT(time-values)',
        'A','WAIT(0.6)','L3','A','WAIT(0.6)','SCREENSHOT(motion)',
        'A','WAIT(0.6)','L3*3','A','WAIT(0.6)','SCREENSHOT(ride)','CLOSE']
    recipe = out/'recipe.toml'
    stages = ['initial', 'overrides', 'existing-srm', 'native-saves', 'srm-over-native']
    recipe.write_text('schema_version = 1\n'+''.join(
        '\n[[samples]]\nsuffix = '+json.dumps(s)+'\nsequence = '+json.dumps(sequence)+'\n' for s in stages))
    screens = Screens()
    manifest = {'core_sha256':hashlib.sha256(args.core.read_bytes()).hexdigest(),
        'recipe_sha256':hashlib.sha256(recipe.read_bytes()).hexdigest(), 'stages':{}, 'status':'running'}
    if (out/'coverage.json').exists():
        previous = json.loads((out/'coverage.json').read_text())
        if any(previous[key]!=manifest[key] for key in ['core_sha256','recipe_sha256']):
            raise RuntimeError('Core/recipe changed; choose a new output directory')
        manifest = previous
    native = out/'native-inputs'
    expected_times = [5,99,51,30,60]
    records = []
    paths = {}
    for stage in stages:
        options = {g:{'sm2_initial_nvram_setup':'enabled', 'sm2_nvram_settings':'disabled'} for g in GAMES}
        if stage == 'overrides':
            for g in GAMES:
                options[g]['sm2_nvram_settings']='enabled'
                for i,value in enumerate(expected_times): options[g][f'sm2_nvram_{g}_checkpoint_{i}']=str(value)
                options[g][f'sm2_nvram_{g}_motion_angle']='25.5'
                if g != 'powsledr': options[g][f'sm2_nvram_{g}_ride_id']='red' if g=='powsledm' else 'black'
        path = out/(stage+'-options.json'); path.write_text(json.dumps(options,indent=2)+'\n')
        prior = manifest['stages'].get(stage)
        attempt = max([int(p.name.rsplit('-',1)[1]) for p in out.glob(stage+'-attempt-*') if p.is_dir()],default=0)+1
        run = Path(prior['run']) if prior else out/f'{stage}-attempt-{attempt:02d}'
        cmd = [sys.executable,str(ROOT/'scripts/test-retroarch-netpacket.py'),
            '--retroarch',str(Path.home()/'Retro/Apps/RetroArch/Nightly/RetroArch (ARM).app/Contents/MacOS/RetroArch'),
            '--core',str(args.core),'--rom',str(integrity.DEFAULT_ROM_DIR/'powsledm.zip'),
            '--relay-rom',str(integrity.DEFAULT_ROM_DIR/'powsledr.zip'),
            '--slave-rom',str(integrity.DEFAULT_ROM_DIR/'powsled.zip'),
            '--system-assets',str(ROOT/'build-libretro-gpu/libretro/system/sm2-emu'),
            '--set-name','powsledm','--cabinets','3','--operator-recipe',str(recipe),
            '--sample',stage,'--output',str(run),'--core-options-override',str(path),
            '--startup-wait','5','--settle','18','--port','55435']
        if stage in ['overrides','existing-srm']:
            cmd += ['--baseline-run',str(paths['initial' if stage=='overrides' else 'overrides'])]
        elif stage == 'native-saves': cmd += ['--native-nvram-baseline',str(native)]
        elif stage == 'srm-over-native':
            cmd += ['--baseline-run',str(paths['overrides']),'--native-nvram-baseline',str(out/'conflicting-native')]
        (out/(stage+'-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
        print(f'[{stages.index(stage)+1}/{len(stages)}] {stage}',flush=True)
        if not prior:
            with (out/(run.name+'.log')).open('w') as log:
                subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        result = json.loads((run/'result.json').read_text())
        if (result['status']!='ok' or result['residual_processes']
                or result['core_sha256'] != manifest['core_sha256']
                or any(i['exit_code']!=0 or i['forced_kill'] or not i['native_link_ready']
                       for i in result['instances'])): raise RuntimeError('Lifecycle/link failed')
        for role,g in zip(ROLES,GAMES):
            save = integrity.find_saves(run/role,g)[0]
            _, backup, eeprom = integrity.decode(save,g)
            initial = (ROOT/'build-libretro-gpu/validation/power-sled-integrity-20261009/initial-images'/f'{g}.bin').read_bytes()
            wanted = bytearray(initial[:16384])
            times = [49,35,35,30,30] if stage=='initial' else expected_times
            motion = 380 if stage=='initial' else 255
            ride = 0 if stage=='initial' or g=='powsledr' else (1 if g=='powsledm' else 2)
            for base in [0,256,512]:
                for i,value in enumerate(times): wanted[base+10+2*i:base+12+2*i]=value.to_bytes(2,'little')
                wanted[base+26:base+28]=motion.to_bytes(2,'little')
                wanted[base+8]=ride
            if any(backup[b:b+28]!=wanted[b:b+28] for b in [0,256,512]):
                raise RuntimeError(f'{stage}/{g}: selected settings not persistent')
            book = {o for b in [768,1024,1280] for o in range(b,b+52)}
            if any(a!=b for o,(a,b) in enumerate(zip(backup,wanted)) if o not in book) or eeprom!=initial[16384:]:
                raise RuntimeError(f'{stage}/{g}: unrelated bytes/EEPROM changed')
            shots = run/role/'screenshots'
            if [screens.number(shots/'time-values.png',f'checkpoint_{i}') for i in range(5)] != times:
                raise RuntimeError('Visible Checkpoints do not match')
            if screens.number(shots/'motion.png','motion') != motion: raise RuntimeError('Visible Motion Angle does not match')
            if g!='powsledr' and screens.ride(shots/'ride.png',g)!=ride: raise RuntimeError('Visible Ride ID does not match')
            logtext = Path(next(i['log'] for i in result['instances'] if i['role']==role)).read_text()
            seeded = 'Applied automatic initial NVRAM setup before the first frame' in logtext
            if seeded != (stage=='initial'): raise RuntimeError('Automatic seeding violated save precedence')
            records.append({'stage':stage,'set':g,'checkpoints':times,'motion_tenths':motion,
                'ride_byte':ride,'initial_seeded':seeded,'srm':str(save),
                'srm_sha256':hashlib.sha256(save.read_bytes()).hexdigest(),
                'screenshots':[{'path':str(shots/name),
                    'sha256':hashlib.sha256((shots/name).read_bytes()).hexdigest()}
                    for name in ['time-values.png','motion.png','ride.png']],
                'settings_and_unrelated_bytes':'Verified','visible_values':'Verified In RetroArch'})
            if stage=='overrides':
                for directory, body in [(native/role, backup+eeprom),
                                        (out/'conflicting-native'/role, initial)]:
                    directory.mkdir(parents=True,exist_ok=True)
                    (directory/f'{g}.nv').write_bytes(body[:16384])
                    (directory/f'{g}.eeprom').write_bytes(body[16384:])
        manifest['stages'][stage] = {'status':'validated','run':str(run)}
        paths[stage] = run
        manifest['records']=records
        (out/'coverage.json').write_text(json.dumps(manifest,indent=2)+'\n')
    manifest['status']='options_and_initial_save_precedence_verified_in_retroarch'
    (out/'coverage.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Passed 5 stages / 15 program records',flush=True)


if __name__ == '__main__': main()
