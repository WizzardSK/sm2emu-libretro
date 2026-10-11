#!/usr/bin/env python3
"""Apply approved BEL calibration to the existing initial template only."""
import json
import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    helpers = runpy.run_path(str(ROOT / 'scripts/generate-initial-nvram-templates.py'))
    calibration = json.loads((ROOT / 'data/bel-calibration-defaults.json').read_text())['calibration']
    if calibration != [0, 0, 0, 0, 255, 255, 255, 255]:
        raise ValueError('BEL upstream mapping requires MIN 00 and DEL FF on every axis')
    path = ROOT / 'src/libretro/initial_nvram_templates.inc'
    text = path.read_text()
    match = re.search(r'static constexpr u8 kBel\[\] = \{(.*?)\n\};', text, re.S)
    packed = bytes(int(value, 16) for value in re.findall(r'0x([0-9a-f]{2})', match[1]))
    body = bytearray()
    offset = 0
    while offset < len(packed):
        command = packed[offset]
        offset += 1
        count = (command & 127) + 1
        if command & 128:
            body.extend(bytes([packed[offset]]) * count)
            offset += 1
        else:
            body.extend(packed[offset:offset + count])
            offset += count
    if len(body) != 16512:
        raise ValueError('Invalid BEL template size')
    for base in (16384, 16448):
        body[base + 0x17:base + 0x1f] = bytes(calibration)
        checksum = (12 + sum(int.from_bytes(body[i:i + 2], 'little')
                              for i in range(base + 2, base + 64, 2))) & 65535
        body[base:base + 2] = checksum.to_bytes(2, 'little')
    packed = helpers['encode'](body)
    replacement = 'static constexpr u8 kBel[] = {\n' + helpers['format_bytes'](packed) + '\n};'
    text = text[:match.start()] + replacement + text[match.end():]
    crc = helpers['crc16_ccitt'](body)
    text = re.sub(r'("bel", kBel, std::size\(kBel\), )0x[0-9a-f]+',
                  lambda m: m[1] + f'0x{crc:04x}', text)
    path.write_text(text)

if __name__ == '__main__':
    main()
