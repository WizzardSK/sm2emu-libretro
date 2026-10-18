#!/usr/bin/env python3
"""Bounded linked Power Sled gameplay probe through the existing RetroArch runner.

Retains staged screenshots, actual frontend PCM and scripted cabinet inputs.
Success of the runner is communication/lifecycle evidence, not gameplay proof.
"""
import argparse
import array
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
from power_sled_campaign import GAMES, ROLES

ROOT = Path(__file__).resolve().parent.parent
ROM_DIR = Path('/Volumes/MacBook External Drive/Retro/_Media/Sega - _Arcade (Model 2)/roms')


def race_replay(path, role, frames=21600, sweep=False, repeat=False, manual=False):
    """Native operator sequence followed by independent rider handle phases.

    Frames are local frontend callbacks, not wall-clock or link synchronization.
    Relay receives no scripted inputs. Never writes calibration or native RAM.
    Y records compensate the inverted frontend polarity to retain native commands.
    """
    pulses = {'host': [(2160,2196,0,8), (2880,2916,1,8), (3360,3396,1,8),
                       (4080,4116,0,3)],
              'client1': [], 'client2': [(1860,1896,0,0)]}[role]
    if repeat:
        # Let the first race and post-race sequence finish before replaying
        # the same native operator sequence. No reset or RAM forcing.
        pulses += [(first+18000,last+18000,port,button)
                   for first,last,port,button in list(pulses)]
        frames = max(frames, 30000)
    phases = [(5100,5700,0,26000,2000,'p1-right'),
              (5700,6300,0,2000,26000,'p1-left'),
              (6600,7200,1,26000,2000,'p2-right'),
              (7200,7800,1,2000,26000,'p2-left')]
    if sweep:
        phases = [(5100,5700,0,'right','p1-right'),
                  (5700,6300,0,'left','p1-left'),
                  (6600,7200,1,'right','p2-right'),
                  (7200,7800,1,'left','p2-left')]
    movie = bytearray(struct.pack('<6I',0x42535632,1,0,0,1,0)+bytes(16))
    for frame in range(frames):
        movie += struct.pack('<BH',0,96)
        for port in range(2):
            pressed = {button for first,last,target,button in pulses
                       if first<=frame<last and port==target}
            right = left = 0
            if manual and role != 'client1':
                # Existing calibrated command zones were measured by the prior
                # RetroArch handlebar sweep. Raw ADC 112 selects Manual;
                # raw 128 lies between both response zones. No endpoint edits.
                selection_frame = frame % 18000 if repeat else frame
                right = round((112 if selection_frame < 3500 else 128) * 65535 / 255 - 32768)
                left = 0
            if role != 'client1':
                for phase in phases:
                    first,last,rider = phase[:3]
                    if not manual and first<=frame<last and port==rider:
                        if sweep:
                            step=(frame-first)%300
                            value=round((step if step<150 else 299-step)*32767/149)
                            right,left=(value,0) if phase[3]=='right' else (0,value)
                        else:
                            right,left=phase[3:5]
            if not manual and (right or left):
                right = max(-32768,min(32767,2*right-32767))
                left = max(-32768,min(32767,2*left-32767))
            values = [(1,0,button,int(button in pressed)) for button in range(16)]
            values += [(5,index,axis,max(-32768,min(32767,-(left if index==0 else right))) if axis==1 else 0)
                       for index in range(2) for axis in range(2)]
            values += [(5,2,button,0) for button in range(16)]
            values += [(2,0,button,0) for button in range(4)]
            values += [(4,0,button,0) for button in (2,3,6,7,13,14,15,16)]
            for device,index,button,value in values:
                movie += struct.pack('<4BHh',port,device,index,0,button,value)
        movie += b'f'
    path.write_bytes(movie)
    return {'frames':frames,'digital_pulses':pulses,
            'analog_phases':phases if role!='client1' and not manual else [],
            'handlebar_sweep':sweep,
            'repeat_race':repeat,
            'manual_mode':manual,
            'manual_adc_selection':112 if manual else None,
            'manual_adc_neutral':128 if manual else None,
            'otherwise_released':not manual}


def race_qualification(args):
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    baseline=args.baseline or ROOT/'build-libretro-gpu/validation/power-sled-audio-integration-20261009/run'
    replay_map={};records={}
    for role in ROLES:
        movie=out/f'{role}.replay'
        records[role]=race_replay(movie,role,sweep=args.handlebar_sweep,
                                  repeat=args.repeat_race,manual=args.manual_mode)
        records[role]['sha256']=hashlib.sha256(movie.read_bytes()).hexdigest()
        replay_map[role]=str(movie)
    mapping=out/'replays.json';mapping.write_text(json.dumps(replay_map,indent=2)+'\n')
    options={game:{'sm2_initial_nvram_setup':'enabled','sm2_nvram_settings':'enabled',
                   f'sm2_automatic_network_{game}':value}
             for game,value in zip(GAMES,('2','r','1'))}
    option_path=out/'options.json';option_path.write_text(json.dumps(options,indent=2)+'\n')
    # Only observations use the operator recipe; every input comes from BSV.
    sequence=['SCREENSHOT(linked-boot)']
    if args.manual_mode and not args.repeat_race:
        # The final placement is brief and was missed by 15-second captures.
        # Retain the qualified dense observation window without new inputs.
        sequence += ['WAIT(115)']
        for i in range(1,101):
            sequence += ['WAIT(0.5)',f'SCREENSHOT(end-{i:03d})']
        sequence += ['WAIT(90)','SCREENSHOT(post-race)']
    else:
        for i in range(1,27 if args.repeat_race else 19):
            sequence += ['WAIT(15)',f'SCREENSHOT(race-{i:02d})']
    sequence += ['CLOSE']
    recipe=out/'recipe.toml';recipe.write_text('schema_version = 1\n\n[[samples]]\nsuffix = "race"\nsequence = '+json.dumps(sequence)+'\n')
    cmd=[sys.executable,str(ROOT/'scripts/test-retroarch-netpacket.py'),
         '--retroarch',str(Path.home()/'Retro/Apps/RetroArch/Nightly/RetroArch (ARM).app/Contents/MacOS/RetroArch'),
         '--core',str(args.core),'--rom',str(ROM_DIR/'powsledm.zip'),
         '--relay-rom',str(ROM_DIR/'powsledr.zip'),'--slave-rom',str(ROM_DIR/'powsled.zip'),
         '--system-assets',str(Path.home()/'Retro/_Media/_Multi (RetroArch)/system/sm2-emu'),
         '--set-name','powsledm','--cabinets','3','--operator-recipe',str(recipe),
         '--sample','race','--baseline-run',str(baseline),'--output',str(out/'run'),
         '--core-options-override',str(option_path),'--input-replay-map',str(mapping),
         '--record-audio','--startup-wait','5','--settle','18','--port',str(args.port)]
    if args.allow_existing_retroarch:
        cmd.append('--allow-existing-retroarch')
    plan={'command':cmd,'core_sha256':hashlib.sha256(args.core.read_bytes()).hexdigest(),
          'replays':records,'status':'prepared_requires_runtime_and_visual_review',
          'no_calibration_or_ram_edits':True,'backend':'SM2-Emu Libretro In RetroArch Only'}
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    if args.prepare_only:
        print('Prepared race replay and exact command:',out/'plan.json',flush=True)
        return
    print('Running linked race with independent BSV input for each program',flush=True)
    with (out/'runner.log').open('w') as log:
        subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
    plan['runtime']=json.loads((out/'run/result.json').read_text())
    plan['status']='captured_requires_gameplay_review'
    (out/'summary.json').write_text(json.dumps(plan,indent=2)+'\n')


def replay(path, both_riders=False, entry_only=False):
    # Same RetroArch 1.22 v1 movie records as smoke-retroarch.py, including
    # its documented 16-byte header padding. Values are actual trigger input.
    movie = bytearray(struct.pack('<6I',0x42535632,1,0,0,1,0)+bytes(16))
    pulses = [(2100,2112,15),(2200,2212,8),  # Enter Test, then leave at Exit.
              (2400,2412,2),(2450,2462,2),  # Common coin inputs, if applicable.
              (2500,2512,0),(2600,2612,8),(2700,2712,3),
              (3100,3112,0),(3200,3212,8),(3300,3312,3)]
    if both_riders:
        for first in range(3600,9000,240):
            pulses += [(first,first+12,0),(first+30,first+42,8),
                       (first+60,first+72,1),(first+90,first+102,9)]
    if entry_only:
        # CALL is an attendant/abort input, not a generic confirmation pulse.
        # Try Entry twice, then leave the introduction uninterrupted.
        pulses = [(2400,2412,0),(2700,2712,0)]
    for frame in range(9600):
        right = left = 0 if entry_only else 16384
        if frame>=3400:
            right,left = (18400,14400) if (frame//180)%2==0 else (14400,18400)
        movie += struct.pack('<BH',0,96)
        for port in range(2):
            values = [(1,0,button,int((port==0 or entry_only and both_riders) and button in pressed)) for button in range(16)]
            values += [(5,index,axis,0) for index in range(2) for axis in range(2)]
            values += [(5,2,button,(right if button==13 else left) if (port==0 or entry_only and both_riders) and button in (12,13) else 0)
                       for button in range(16)]
            values += [(2,0,button,0) for button in range(4)]
            values += [(4,0,button,0) for button in (2,3,6,7,13,14,15,16)]
            for device,index,button,value in values:
                movie += struct.pack('<4BHh',port,device,index,0,button,value)
        movie += b'f'
    path.write_bytes(movie)
    return pulses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--main-ride',choices=('silver','red','black'),default='red')
    parser.add_argument('--slave-ride',choices=('silver','red','black'),default='black')
    parser.add_argument('--both-riders',action='store_true',help='Drive both local riders; --entry-only omits Call')
    parser.add_argument('--entry-only',action='store_true',help='Entry-only attempt with native released handles, no Test or repeated attendant Call')
    parser.add_argument('--race-qualification',action='store_true',help='Current native Start sequence and independent BSV rider Y axes')
    parser.add_argument('--handlebar-sweep',action='store_true',help='Sweep each handle independently across the full input range during the race')
    parser.add_argument('--repeat-race',action='store_true',help='Repeat native operator inputs after 18000 frontend frames to check post-race recovery')
    parser.add_argument('--manual-mode',action='store_true',help='Select Manual through the previously measured handlebar zone, then hold native neutral handles')
    parser.add_argument('--allow-existing-retroarch',action='store_true',help='Allow the isolated race test alongside an already open RetroArch')
    parser.add_argument('--prepare-only',action='store_true',help='Prepare the race fixtures and command without launching')
    parser.add_argument('--port',type=int,default=55496)
    parser.add_argument('--core',type=Path,default=Path.home()/'Library/Application Support/RetroArch/cores/sm2_libretro.dylib')
    args = parser.parse_args()
    if args.repeat_race and not args.race_qualification:
        parser.error('--repeat-race requires --race-qualification')
    if args.manual_mode and (not args.race_qualification or args.handlebar_sweep):
        parser.error('--manual-mode requires --race-qualification and excludes --handlebar-sweep')
    if args.allow_existing_retroarch and not args.race_qualification:
        parser.error('--allow-existing-retroarch requires --race-qualification')
    if args.race_qualification:
        race_qualification(args)
        return
    if args.prepare_only:
        parser.error('--prepare-only requires --race-qualification')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    proof=json.loads((ROOT/'build-libretro-gpu/validation/power-sled-options-20261009/coverage.json').read_text())
    baseline=args.baseline or Path(proof['stages']['initial']['run'])
    movie=out/'cabinet-inputs.replay';pulses=replay(movie,args.both_riders,args.entry_only)
    options={game:{'sm2_initial_nvram_setup':'enabled','sm2_nvram_settings':'enabled'} for game in GAMES}
    for game in GAMES:
        if game!='powsledr':options[game][f'sm2_nvram_{game}_ride_id']=args.main_ride if game=='powsledm' else args.slave_ride
    option_path=out/'options.json';option_path.write_text(json.dumps(options,indent=2)+'\n')
    sequence=['SCREENSHOT(linked-boot)']
    for i in range(1,7): sequence += ['WAIT(10.0)',f'SCREENSHOT(gameplay-{i:02d})']
    sequence += ['CLOSE']
    recipe=out/'recipe.toml';recipe.write_text('schema_version = 1\n\n[[samples]]\nsuffix = "gameplay"\nsequence = '+json.dumps(sequence)+'\n')
    cmd=[sys.executable,str(ROOT/'scripts/test-retroarch-netpacket.py'),
         '--retroarch',str(Path.home()/'Retro/Apps/RetroArch/Nightly/RetroArch (ARM).app/Contents/MacOS/RetroArch'),
         '--core',str(args.core),'--rom',str(ROM_DIR/'powsledm.zip'),
         '--relay-rom',str(ROM_DIR/'powsledr.zip'),'--slave-rom',str(ROM_DIR/'powsled.zip'),
         '--system-assets',str(ROOT/'build-libretro-gpu/libretro/system/sm2-emu'),
         '--set-name','powsledm','--cabinets','3','--operator-recipe',str(recipe),
         '--sample','gameplay','--baseline-run',str(baseline),'--output',str(out/'run'),
         '--core-options-override',str(option_path),'--input-replay',str(movie),
         '--record-audio','--startup-wait','5','--settle','18','--port','55435']
    manifest={'command':cmd,'core_sha256':hashlib.sha256(args.core.read_bytes()).hexdigest(),
              'input_replay_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),
              'input_frames':9600,'digital_pulses':pulses,'neutral_triggers':0 if args.entry_only else 16384,
              'ride_colors':{'powsledm':args.main_ride,'powsled':args.slave_ride},
              'both_riders':args.both_riders,
              'entry_only':args.entry_only,
              'second_rider_analog':args.entry_only and args.both_riders,
              'handlebar_variation_from_frame':3400,'handlebar_values':[14400,18400]}
    (out/'plan.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Running bounded three-program gameplay probe with PCM recording',flush=True)
    with (out/'runner.log').open('w') as log:
        subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
    spec=importlib.util.spec_from_file_location('smoke_retroarch',ROOT/'scripts/smoke-retroarch.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    results=[]
    for role,game in zip(ROLES,GAMES):
        root=out/'run'/role
        params,pcm,format=module.read_recording(root/'audio.wav')
        samples=array.array('h',pcm)
        log=(out/'run'/f'{role}.log').read_text(errors='replace')
        shots=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((root/'screenshots').glob('*.png'))]
        results.append({'set':game,'role':role,'audio_rate':params.framerate,
            'audio_seconds':params.nframes/params.framerate,'audio_peak':max(map(abs,samples),default=0),
            'audio_nonzero_samples':sum(value!=0 for value in samples),'recording_format':format,
            'audio_driver_started':'[Audio] Started' in log and 'failed_to_start_audio_driver' not in log,
            'pcm_sha256':hashlib.sha256(pcm).hexdigest(),'screenshots':shots})
    manifest['results']=results
    manifest['runtime']=json.loads((out/'run/result.json').read_text())
    manifest['status']='captured_requires_gameplay_review'
    (out/'summary.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps([{key:value for key,value in result.items() if key!='screenshots'}
                      for result in results],indent=2),flush=True)


if __name__=='__main__':main()
