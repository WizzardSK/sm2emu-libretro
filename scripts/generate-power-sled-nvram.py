#!/usr/bin/env python3
"""Generate approved Power Sled options and templates from qualified core images.

Only generated Power Sled sections are replaced; existing game data is retained.
The retained RetroArch qualification manifest pins each independent image.
"""
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / 'build-libretro-gpu/validation/power-sled-integrity-20261009/coverage.json'


def replace_section(text, name, body, before):
    begin, end = f'// BEGIN {name}', f'// END {name}'
    section = f'{begin}\n{body}\n{end}\n'
    if begin in text:
        start = text.index(begin)
        stop = text.index(end, start) + len(end) + 1
        return text[:start] + section + text[stop:]
    pos = text.index(before)
    return text[:pos] + section + '\n' + text[pos:]


def main():
    evidence = json.loads(EVIDENCE.read_text())
    if evidence['status'] != 'native_integrity_and_per_set_initial_images_validated':
        raise ValueError('Initial images have not passed the target-core campaign')
    helpers = runpy.run_path(str(ROOT / 'scripts/generate-initial-nvram-templates.py'))
    arrays, entries, templates, template_entries = [], [], [], []
    fields = [('ride_id', 'RIDE ID', 8, ['silver', 'red', 'black'], ['Silver', 'Red', 'Black'])]
    fields += [(f'checkpoint_{i}', f'CHECKPOINT {i}', 10+2*i,
                [str(n) for n in range(5, 100)], [str(n) for n in range(5, 100)]) for i in range(5)]
    fields += [('motion_angle', 'MOTION ANGLE', 26,
                [f'{n/10:.1f}' for n in range(100, 451, 5)],
                [f'{n/10:.1f}' for n in range(100, 451, 5)])]
    defaults = ['silver', '49', '35', '35', '30', '30', '38.0']
    for index, (suffix, label, offset, keys, labels) in enumerate(fields):
        width = 1 if suffix == 'ride_id' else 2
        raw = list(range(3)) if width == 1 else ([int(float(k)*10) for k in keys]
                     if suffix == 'motion_angle' else [int(k) for k in keys])
        patches = [f'    {{{offset+copy*256+byte}, 0xff}},' for copy in range(3) for byte in range(width)]
        arrays += [f'static constexpr Patch kPowerPatches{index}[] = {{\n'+ '\n'.join(patches)+'\n};']
        desired = b''.join(n.to_bytes(width, 'little')*3 for n in raw)
        arrays += [f'static constexpr u8 kPowerDesired{index}[] = {{\n'+helpers['format_bytes'](desired)+'\n};']
        values = [f'    {{"{key}", "{value}", kPowerDesired{index} + {i*width*3}}},'
                  for i, (key, value) in enumerate(zip(keys, labels))]
        arrays += [f'static constexpr Value kPowerValues{index}[] = {{\n'+ '\n'.join(values)+'\n};']
    for game in ['powsled', 'powsledm', 'powsledr']:
        image = next(r for r in evidence['initial_images'] if r['set'] == game)
        body = Path(image['initial_payload']).read_bytes()
        if len(body) != 16512 or hashlib.sha256(body).hexdigest() != image['initial_payload_sha256']:
            raise ValueError(f'Qualified image missing or changed: {game}')
        symbol = 'kPower' + game.capitalize()
        templates += [f'static constexpr u8 {symbol}[] = {{\n'+helpers['format_bytes'](helpers['encode'](body))+'\n};']
        template_entries += [f'    {{"{game}", {symbol}, std::size({symbol}), 0x{helpers["crc16_ccitt"](body):04x}}},']
        for index, (suffix, label, offset, keys, labels) in enumerate(fields):
            if game == 'powsledr' and suffix == 'ride_id':
                continue
            help_text = f'Set {label} in the game\'s operator NVRAM. Applied at startup when NVRAM Settings is enabled.'
            if suffix.startswith('checkpoint'):
                help_text += ' Time extension in seconds, from 5 to 99.'
            elif suffix == 'motion_angle':
                help_text += ' Native cabinet motion limit in degrees; this does not calibrate the controls.'
            else:
                help_text += ' Silver is the native initialization value. Program roles and conditional ID assignment are unchanged.'
            entries += [f'    {{"{game}", "{suffix}", "{label}", "{help_text}", "{defaults[index]}", '
                        f'kPowerValues{index}, std::size(kPowerValues{index}), kPowerPatches{index}, std::size(kPowerPatches{index})}},']
    path = ROOT / 'src/libretro/nvram_settings_data.inc'
    text = replace_section(path.read_text(), 'POWER SLED ARRAYS', '\n\n'.join(arrays), 'static constexpr Option kOptions[] = {')
    if '// BEGIN POWER SLED OPTIONS' in text:
        text = replace_section(text, 'POWER SLED OPTIONS', '\n'.join(entries), '')
    else:
        pos = text.index('\n};', text.index('static constexpr Option kOptions[] = {'))
        text = text[:pos]+'\n// BEGIN POWER SLED OPTIONS\n'+'\n'.join(entries)+'\n// END POWER SLED OPTIONS'+text[pos:]
    path.write_text(text)
    path = ROOT / 'src/libretro/initial_nvram_templates.inc'
    text = replace_section(path.read_text(), 'POWER SLED IMAGES', '\n\n'.join(templates), 'static constexpr Template kTemplates[] = {')
    if '// BEGIN POWER SLED TEMPLATES' in text:
        text = replace_section(text, 'POWER SLED TEMPLATES', '\n'.join(template_entries), '')
    else:
        pos = text.index('\n};', text.index('static constexpr Template kTemplates[] = {'))
        text = text[:pos]+'\n// BEGIN POWER SLED TEMPLATES\n'+'\n'.join(template_entries)+'\n// END POWER SLED TEMPLATES'+text[pos:]
    path.write_text(text)
    print('Generated 20 approved options and 3 independently qualified initial templates')


if __name__ == '__main__':
    main()
