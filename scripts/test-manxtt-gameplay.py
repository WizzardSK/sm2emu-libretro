#!/usr/bin/env python3
"""Bounded Manx TT frontend campaign using the existing isolated runners.

Two native linked topologies plus the non-network DX program. Replays contain
only frontend input; no ROM/state/RAM/calibration writes. Captures need visual
review before gameplay is qualified. No physical-controller claim is made.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
ROM_DIR = Path('/Volumes/MacBook External Drive/Retro/_Media/Sega - _Arcade (Model 2)/roms')
CASES = [('manxtt-relay', 'manxtt', 3), ('manxttc-pair', 'manxttc', 2),
         ('manxttdx-single', 'manxttdx', 1)]


def replay(path, role, frames=24000, deluxe=False):
    # Same padded RetroArch 1.22 v1 records as smoke-retroarch.py and the
    # established Power Sled replay runner. Relay receives released inputs.
    movie = bytearray(struct.pack('<6I', 0x42535632, 1, 0, 0, 1, 0) + bytes(16))
    for frame in range(frames):
        pressed = set()
        rider = role != 'client2'
        if rider:
            if 3000 <= frame < 4500 and frame % 180 < 18:
                pressed.add(2)  # Coin.
            if 3400 <= frame < 5100 and frame % 180 < 18:
                pressed.add(3)  # Start / VR / selection confirmation.
            if deluxe and 7800 <= frame < 9000 and frame % 180 < 18:
                pressed.add(3)  # Confirm after the DX operation tutorial.
            if 5400 <= frame < 7200 and frame % 240 < 18:
                pressed.add(11)  # Sequential shift up.
        movie += struct.pack('<BH', 0, 96)
        for port in range(2):
            active = rider and port == 0
            bank = 0
            if active and frame >= 5400:
                bank = (5000 if (frame // 480) % 2 == 0 else -5000)
                if role == 'client1':
                    bank = -bank
                if deluxe and 6600 <= frame < 7200:
                    bank = 30000 if frame < 6900 else -30000
            values = [(1, 0, button, int(active and button in pressed))
                      for button in range(16)]
            values += [(5, index, axis, bank if index == 0 and axis == 0 else 0)
                       for index in range(2) for axis in range(2)]
            throttle = active and frame >= 3600 and not (deluxe and 7200 <= frame < 8400)
            brake = active and deluxe and 7200 <= frame < 8400
            values += [(5, 2, button, 32767 if (throttle and button == 13) or (brake and button == 12) else 0)
                       for button in range(16)]
            values += [(2, 0, button, 0) for button in range(4)]
            values += [(4, 0, button, 0) for button in (2, 3, 6, 7, 13, 14, 15, 16)]
            for device, index, button, value in values:
                movie += struct.pack('<4BHh', port, device, index, 0, button, value)
        movie += b'f'
    path.write_bytes(movie)
    return {'path': str(path), 'sha256': hashlib.sha256(movie).hexdigest(),
            'frames': frames, 'rider': role != 'client2',
            'coin_frames': [3000, 4500], 'start_frames': [3400, 5100],
            'throttle_from': 3600, 'shift_up_frames': [5400, 7200],
            'bank_from': 5400, 'bank_amplitude': 5000,
            'deluxe_tutorial_throttle_release_and_full_brake_frames': [7200, 8400] if deluxe else None,
            'deluxe_tutorial_full_bank_sweep_frames': [6600, 7200] if deluxe else None,
            'no_test_service_or_calibration': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--case', action='append', choices=[c[0] for c in CASES])
    p.add_argument('--core', type=Path, default=Path.home()/'Library/Application Support/RetroArch/cores/sm2_libretro.dylib')
    p.add_argument('--retroarch', type=Path, default=Path.home()/'Retro/Apps/RetroArch/Nightly/RetroArch (ARM).app/Contents/MacOS/RetroArch')
    p.add_argument('--rom-dir', type=Path, default=ROM_DIR)
    p.add_argument('--port', type=int, default=55580)
    p.add_argument('--prepare-only', action='store_true')
    args = p.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    core_hash = hashlib.sha256(args.core.read_bytes()).hexdigest()
    plan = {'core_sha256': core_hash, 'cases': [],
            'scope': 'Native RetroArch gameplay observation, not physical device or exhaustive firmware qualification.'}
    for index, (name, game, cabinets) in enumerate(CASES):
        if args.case and name not in args.case:
            continue
        root = out/name
        root.mkdir()
        roles = ['host', 'client1', 'client2'][:cabinets]
        replays = {role: replay(root/(role+'.replay'), role, deluxe=cabinets == 1) for role in roles}
        mapping = root/'replays.json'
        mapping.write_text(json.dumps({r: v['path'] for r, v in replays.items()}, indent=2)+'\n')
        if cabinets > 1:
            command = [sys.executable, str(ROOT/'scripts/test-retroarch-netpacket.py'),
                       '--retroarch', str(args.retroarch), '--core', str(args.core),
                       '--rom', str(args.rom_dir/(game+'.zip')), '--set-name', game,
                       '--system-assets', str(Path.home()/'Retro/_Media/_Multi (RetroArch)/system/sm2-emu'),
                       '--cabinets', str(cabinets), '--automatic-network',
                       '--input-replay-map', str(mapping), '--record-audio',
                       '--capture-screenshots', '--screenshot-samples', '20', '--screenshot-gap', '8',
                       '--settle', '18', '--startup-wait', '5', '--port', str(args.port+index),
                       '--output', str(root/'run')]
        else:
            # DX has its own catalogue without Link Type; do not force parent
            # link fields into this native program. The single-game runner
            # supplies the same replay, PCM, SRAM and a final image.
            command = [sys.executable, str(ROOT/'scripts/smoke-retroarch.py'),
                       '--retroarch', str(args.retroarch), '--core', str(args.core),
                       '--system', str(Path.home()/'Retro/_Media/_Multi (RetroArch)/system'),
                       '--rom', str(args.rom_dir/(game+'.zip')), '--set-name', game,
                       '--sequential-inputs', '--input-replay', replays['host']['path'],
                       '--renderer', 'software', '--av-timing', '60hz', '--max-frames', '11000',
                       '--timeout', '230', '--output', str(root/'run')]
        case = {'name': name, 'game': game, 'cabinets': cabinets, 'replays': replays,
                'command': command, 'status': 'prepared'}
        plan['cases'].append(case)
        (root/'command.json').write_text(json.dumps(command, indent=2)+'\n')
    (out/'plan.json').write_text(json.dumps(plan, indent=2)+'\n')
    if args.prepare_only:
        print('Prepared:', out/'plan.json', flush=True)
        return
    for case in plan['cases']:
        print('Running:', case['name'], flush=True)
        with (out/case['name']/'runner.log').open('w') as log:
            result = subprocess.run(case['command'], stdout=log, stderr=subprocess.STDOUT)
        case['exit_code'] = result.returncode
        case['status'] = 'captured_requires_review' if result.returncode == 0 else 'failed_requires_diagnosis'
        (out/'plan.json').write_text(json.dumps(plan, indent=2)+'\n')
        print(case['name']+': '+case['status'], flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
