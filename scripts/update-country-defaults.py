#!/usr/bin/env python3
"""Apply the approved Export, Europe, USA priority to reviewed Country defaults.

Preserve value order, native labels, encodings and acquired initial images.
Automatic initialization uses these same Option defaults via initial_values().
Run after regenerating nvram_settings_data.inc from older campaign evidence.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def region(value):
    normalized = re.sub('[^a-z]', '', value.lower())
    return {'exp': 'export', 'eur': 'europe', 'us': 'usa'}.get(normalized, normalized)

def main():
    path = ROOT / 'src/libretro/nvram_settings_data.inc'
    text = path.read_text()
    values = {}
    for match in re.finditer(r'static constexpr Value (kValues\w+)\[\] = \{(.*?)\n\};', text, re.S):
        values[match[1]] = re.findall(r'\{"([^"]+)", "([^"]+)"', match[2])
    pattern = r'(\{"([^"]+)", "(?:country|nation)", "[^"]+", "[^"]+", ")([^"]+)(", (kValues\w+),)'
    def update(match):
        choices = values[match[5]]
        preferred = next((key for priority in ('export', 'europe', 'usa')
                          for key, label in choices if region(label) == priority), match[3])
        if preferred != match[3]:
            print(f'{match[2]}: {match[3]} -> {preferred}')
        return match[1] + preferred + match[4]
    text = re.sub(pattern, update, text)
    text = text.replace('Export is the default when the game supports it; USA is the fallback.',
                        'Default priority: Export, Europe, U.S.A., using the first supported region.')
    path.write_text(text)

if __name__ == '__main__':
    main()
