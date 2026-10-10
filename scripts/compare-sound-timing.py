#!/usr/bin/env python3
"""Compare isolated sound-board traces against an already-built pristine upstream.

Uses existing native Ninja build/link settings; does not edit either source tree.
ROMs, object files, executables and traces remain in a new external output folder.
"""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess


def build_probe(source, build, target, probe, output, name):
    line = subprocess.check_output(
        ['ninja', '-C', str(build), '-t', 'commands', target], text=True).splitlines()[-1]
    tokens = shlex.split(line)
    if tokens[:2] != [':', '&&'] or tokens[-2:] != ['&&', ':']:
        raise RuntimeError('Expected a plain CMake Ninja link command')
    command = tokens[2:-2]
    main = [item for item in command if item.endswith('/main.cpp.o')]
    if len(main) != 1 or '-o' not in command:
        raise RuntimeError('Cannot identify the existing main object/output')
    obj, exe = output / f'{name}.o', output / name
    subprocess.run([command[0], '-std=c++20', '-O3', '-I' + str(source / 'src'),
                    '-c', str(probe), '-o', str(obj)], check=True)
    command[command.index(main[0])] = str(obj)
    command[command.index('-o') + 1] = str(exe)
    subprocess.run(command, cwd=build, check=True, capture_output=True)
    return exe


def trace(exe, args, log):
    with log.open('w') as out:
        subprocess.run([str(exe), *map(str, args)], stdout=out,
                       stderr=subprocess.STDOUT, check=True, timeout=60)
    return '\n'.join(line for line in log.read_text().splitlines()
                     if re.match(r'^\d+ ', line))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['adapted-source', 'adapted-build', 'upstream-source',
                'upstream-build', 'rom-directory', 'output']:
        parser.add_argument('--' + key, type=Path, required=True)
    parser.add_argument('--game', action='append', default=[])
    args = parser.parse_args()
    paths = {key: value.resolve() for key, value in vars(args).items() if isinstance(value, Path)}
    output = paths['output']; output.mkdir(parents=True, exist_ok=False)
    source = paths['adapted_source']
    probe = source / 'src/libretro/checks/sound_timing_probe.cpp'
    executables = [build_probe(source, paths['adapted_build'], 'sm2-headless', probe,
                               output, 'adapted'),
                   build_probe(paths['upstream_source'], paths['upstream_build'],
                               'sm2-emu', probe, output, 'pristine')]
    checks = {}
    games = args.game or ['vf2', 'srallyc', 'hotd', 'topskatr']
    for game in [None, *games]:
        name = game or 'synthetic-eight-slots'
        params = [] if game is None else [source / 'data/games.xml',
                  paths['rom_directory'] / f'{game}.zip', game]
        traces = [trace(exe, params, output / f'{kind}-{name}.log')
                  for kind, exe in zip(['adapted', 'pristine'], executables)]
        checks[name] = bool(traces[0]) and traces[0] == traces[1]
    (output / 'comparison.json').write_text(json.dumps(checks, indent=2) + '\n')
    print(json.dumps(checks, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
