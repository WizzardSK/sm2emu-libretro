#!/usr/bin/env python3
"""Verify a bounded Power Sled Motion Angle campaign acquired only in RetroArch.

Pillow is used for exact native value-region comparisons against the visually
reviewed 38.0/38.5 captures. This does not prove complete native RAM integrity
or supply an initial NVRAM template.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('evidence', type=Path)
args = parser.parse_args()
root = args.evidence.resolve()
roles = {'host': 'powsledm', 'client1': 'powsledr', 'client2': 'powsled'}
stages = {'motion-native-default': (380, 'motion-default'),
          'motion-plus-step': (385, 'motion-plus-step'),
          'motion-reload': (385, 'motion-reloaded')}
# Digits only; independent of selected command or residual unit-label pixels.
box = (476, 348, 548, 370)
def pixels(path):
    with Image.open(path) as image:
        assert image.size == (1024, 768), (path, image.size)
        return image.convert('RGB').crop(box).tobytes()
refs = {raw: pixels(root / stage / 'host' / 'screenshots' / f'{shot}.png')
        for stage, (raw, shot) in stages.items() if stage != 'motion-reload'}
assert refs[380] != refs[385], 'Value crop does not distinguish 38.0 from 38.5'
records = []
for stage, (raw, shot) in stages.items():
    run = root / stage
    result = json.loads((run / 'result.json').read_text())
    assert result['status'] == 'ok' and not result['residual_processes'], stage
    assert len(result['operator_saves']) == 3, stage
    for item in result['instances']:
        assert item['exit_code'] == 0 and not item['forced_kill']
        assert item['roster_ready'] and item['native_link_ready']
    for role, game in roles.items():
        backup = run / role / 'samples' / f'{game}.nv'
        data = backup.read_bytes()
        copies = [int.from_bytes(data[0x1a+i:0x1c+i], 'little') for i in (0, 0x100, 0x200)]
        assert copies == [raw]*3, (stage, game, copies)
        screen = run / role / 'screenshots' / f'{shot}.png'
        assert pixels(screen) == refs[raw], (stage, game, 'visible value mismatch')
        if stage == 'motion-plus-step':
            baseline = run / role / 'screenshots' / 'motion-baseline.png'
            assert pixels(baseline) == refs[380], (game, 'default did not reload')
        records.append({'set': game, 'stage': stage, 'value_degrees': raw / 10,
                        'native_copies': copies, 'backup': str(backup),
                        'backup_sha256': hashlib.sha256(data).hexdigest(),
                        'screenshot': str(screen),
                        'screenshot_sha256': hashlib.sha256(screen.read_bytes()).hexdigest()})
summary = {'status': 'passed', 'backend': 'SM2-Emu Libretro In RetroArch Only',
           'value_crop': box, 'records': records,
           'verified': ['Native Use Default 38.0', 'Native Set And Exit',
                        'Fresh Default Reload', 'One Increment To 38.5',
                        'Fresh Edited Value Reload', 'Three Concordant U16 LE Copies'],
           'pending': ['Numeric Limits And Other Representatives', 'Other Operator Settings',
                       'Complete Native Integrity', 'Initial Templates', 'Core Option Review']}
(root / 'motion-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print('Power Sled core Motion Angle: 9 stage/program checks passed')
