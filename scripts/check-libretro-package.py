#!/usr/bin/env python3
"""Validate the contents and checksums of a packaged SM2 Libretro core."""

from __future__ import annotations

import hashlib
import argparse
import json
import tarfile
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('directory', type=Path)
parser.add_argument('binary')
parser.add_argument('--source-archive', type=Path, required=True)
parser.add_argument('--allow-dirty', action='store_true', help='Local review only')
args = parser.parse_args()
root = args.directory.resolve()
binary = args.binary

required = {
    binary,
    "sm2_libretro.info",
    "system/sm2-emu/games.xml",
    "LICENSE",
    "NOTICE",
    "README.md",
    "SOURCE_COMMIT.txt",
    "SOURCE.json",
    "licenses/BSD-3-Clause.txt",
    "licenses/ImGui.txt",
    "SHA256SUMS",
    "licenses/LZMA-SDK.txt",
    "licenses/Musashi.txt",
    "licenses/VulkanMemoryAllocator.txt",
    "licenses/libretro-api.txt",
    "licenses/miniz.txt",
    "licenses/pugixml.txt",
    "licenses/ymfm.txt",
}

if not root.is_dir():
    raise SystemExit(f"package directory not found: {root}")

files = {
    path.relative_to(root).as_posix()
    for path in root.rglob("*")
    if path.is_file()
}
missing = required - files
extra = files - required
assert not missing, f"missing package files: {sorted(missing)}"
assert not extra, f"unexpected package files: {sorted(extra)}"

for name in files:
    assert Path(name).suffix.lower() not in {".zip", ".7z", ".chd", ".iso", ".rom"}, (
        f"game-content-like file in package: {name}"
    )

commit = (root / "SOURCE_COMMIT.txt").read_text(encoding="ascii").strip()
assert re.fullmatch(r"[0-9a-f]{40}", commit), f"invalid source commit: {commit!r}"

info = (root / "sm2_libretro.info").read_text(encoding="utf-8")
assert 'firmware0_path = "sm2-emu/games.xml"' in info
assert 'license = "GPL-3.0-or-later"' in info
assert 'SM2-Emu Libretro' in info and 'modified version' in info
assert 'https://github.com/dmanlfc/sm2-emu' in info
assert 'GNU GENERAL PUBLIC LICENSE' in (root/'LICENSE').read_text()
notice = (root/'NOTICE').read_text()
assert 'Additional terms' in notice and 'SM2-Emu Libretro' in notice
source = json.loads((root/'SOURCE.json').read_text())
assert source['revision'] == commit
assert args.allow_dirty or not source['worktree_dirty'], 'Dirty source is not releasable'
archive = args.source_archive.resolve(strict=True)
assert archive.name == source['archive']
assert hashlib.sha256(archive.read_bytes()).hexdigest() == source['sha256']
with tarfile.open(archive) as tar:
    prefix = 'sm2-emu-libretro/'
    manifest = json.load(tar.extractfile(prefix+'SOURCE_MANIFEST.json'))
    assert manifest['revision'] == commit and manifest['submodules'] == source['submodules']
    assert manifest['worktree_dirty'] == source['worktree_dirty']
    members = {entry.name: entry for entry in tar.getmembers()}
    assert len(members) == len(manifest['files']) + 1
    for name, digest in manifest['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        entry = members[prefix+name]
        if isinstance(digest, dict):
            assert entry.issym() and entry.linkname == digest['symlink'], name
        else:
            assert entry.isfile(), name
            stream = tar.extractfile(entry)
            assert stream and hashlib.sha256(stream.read()).hexdigest() == digest, name
    for name in ['CMakeLists.txt', '.gitmodules', 'LICENSE', 'NOTICE', 'src/libretro/core.cpp']:
        assert name in manifest['files'], name
    for path in source['submodules']:
        assert any(name.startswith(path+'/') for name in manifest['files']), path
    for packaged, original in [('LICENSE','LICENSE'), ('NOTICE','NOTICE'),
            ('sm2_libretro.info','sm2_libretro.info'), ('system/sm2-emu/games.xml','data/games.xml'),
            ('licenses/ImGui.txt','3rdparty/imgui/LICENSE.txt'),
            ('licenses/BSD-3-Clause.txt','licenses/BSD-3-Clause.txt')]:
        assert hashlib.sha256((root/packaged).read_bytes()).hexdigest() == manifest['files'][original], (
            f'Source/package byte mismatch: {packaged} (checkout line endings must match source)'
        )

assert 'savestate = "true"' in info

ET.parse(root / "system/sm2-emu/games.xml")
assert (root / binary).stat().st_size > 0

listed: dict[str, str] = {}
for line in (root / "SHA256SUMS").read_text(encoding="ascii").splitlines():
    digest, separator, name = line.partition("  ")
    assert separator and re.fullmatch(r"[0-9a-f]{64}", digest), f"invalid checksum line: {line!r}"
    assert name not in listed, f"duplicate checksum: {name}"
    listed[name] = digest

hashed_files = files - {"SHA256SUMS"}
assert set(listed) == hashed_files, (
    f"checksum coverage differs: missing={sorted(hashed_files - set(listed))}, "
    f"extra={sorted(set(listed) - hashed_files)}"
)
for name, expected in listed.items():
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    assert actual == expected, f"checksum mismatch: {name}"

print(f"PASS: complete package, {len(files)} files, checksums and licences verified")
