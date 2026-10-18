#!/usr/bin/env python3
"""Package the checked-out source and recursively pinned submodules, without Git metadata."""
import argparse
import hashlib
import io
import os
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-dirty', action='store_true', help='Local review only; never release this snapshot')
    args = parser.parse_args()
    revision = git(ROOT, 'rev-parse', 'HEAD').decode().strip()
    dirty = bool(git(ROOT, 'status', '--porcelain', '--untracked-files=normal'))
    if dirty and not args.allow_dirty:
        parser.error('Source checkout is dirty; commit approved changes before release packaging')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    submodules = {}

    def collect(repo, prefix=Path()):
        entries = git(repo, 'ls-files', '--stage', '-z').split(b'\0')
        tracked = set()
        for entry in entries:
            if not entry: continue
            meta, raw_name = entry.split(b'\t', 1)
            mode, pin, stage = meta.decode().split()
            if stage != '0': raise RuntimeError('Unresolved merge in source checkout')
            name = Path(raw_name.decode())
            tracked.add(name)
            path = repo / name
            relative = prefix / name
            if mode == '160000':
                actual = git(path, 'rev-parse', 'HEAD').decode().strip()
                if actual != pin: raise RuntimeError(f'Submodule pin mismatch: {relative}')
                if git(path, 'status', '--porcelain'):
                    raise RuntimeError(f'Dirty submodule: {relative}')
                submodules[relative.as_posix()] = pin
                collect(path, relative)
            elif path.is_file() or path.is_symlink():
                files[relative.as_posix()] = path
            elif not args.allow_dirty:
                raise RuntimeError(f'Missing tracked source: {relative}')
        if args.allow_dirty and repo == ROOT:
            for raw_name in git(repo, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
                if raw_name:
                    name = Path(raw_name.decode())
                    if name not in tracked: files[(prefix/name).as_posix()] = repo/name

    collect(ROOT)
    manifest = {'revision': revision, 'worktree_dirty': dirty, 'submodules': submodules, 'files': {}}
    for name, path in sorted(files.items()):
        if path.suffix.lower() in {'.zip', '.7z', '.chd', '.iso', '.rom', '.srm', '.state'}:
            raise RuntimeError(f'Unexpected game/save archive in source: {name}')
        if path.is_symlink():
            path.resolve(strict=True).relative_to(ROOT)
        manifest['files'][name] = ({'symlink': os.readlink(path)} if path.is_symlink()
                                   else hashlib.sha256(path.read_bytes()).hexdigest())
    archive = output / f'sm2-libretro-source-{revision}{"-local" if dirty else ""}.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        for name, path in sorted(files.items()):
            tar.add(path, arcname='sm2-emu-libretro/'+name, recursive=False)
        data = (json.dumps(manifest, indent=2)+'\n').encode()
        entry = tarfile.TarInfo('sm2-emu-libretro/SOURCE_MANIFEST.json')
        entry.size = len(data); entry.mode = 0o644
        tar.addfile(entry, io.BytesIO(data))
    descriptor = {key: manifest[key] for key in ['revision', 'worktree_dirty', 'submodules']}
    descriptor.update(archive=archive.name, sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                      repository='https://github.com/Zer0one/sm2-emu-libretro',
                      licence='GPL-3.0-or-later; additional terms in NOTICE')
    (output/'SOURCE.json').write_text(json.dumps(descriptor, indent=2)+'\n')
    print(f'Packaged {len(files)} source files and {len(submodules)} pinned submodules: {archive}')

if __name__ == '__main__': main()
