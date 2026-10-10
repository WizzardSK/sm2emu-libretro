#!/usr/bin/env python3
"""Verify every acquired discrete Power Sled state and native fresh reload.

Requires Pillow. Reference crops were visually reviewed; comparisons cover the
value line only, excluding cursor position. Numeric sampling is handled by the
separate numeric campaign analyzer.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    root = parser.parse_args().evidence.resolve()
    units = ["1-powsledm", "2-powsledr", "3-powsled"]

    def crop(path):
        return Image.open(path).convert("RGB").crop((160, 140, 360, 156)).tobytes()

    refs = root / "commits/1-powsledm"
    colors = {1: crop(refs / "screen-0010.png"),
              2: crop(refs / "screen-0012.png"),
              0: crop(refs / "screen-0014.png")}
    relay = crop(root / "commits/2-powsledr/screen-0010.png")
    export = crop(refs / "screen-0001.png")
    names = {0: "Silver Ride", 1: "Red Ride", 2: "Black Ride"}

    def backup(folder, unit, index):
        b = (root / folder / unit / f"backup-{index:04}.bin").read_bytes()
        assert len(b) == 16384
        return b

    def state(b, offset):
        values = [b[offset + stride] for stride in (0, 256, 512)]
        assert len(set(values)) == 1, values
        return values[0]

    def verify_run(folder):
        manifest = json.loads((root / folder / "manifest.json").read_text())
        assert all(u["returncode"] == 0 and u["probe_ok"] for u in manifest["units"])

    verify_run("commits")
    results = {}
    for unit in units:
        country_cycle = []
        ride_cycle = []
        before = backup("commits", unit, 1)
        for n in range(4):
            visible, committed = 2 + 2*n, 3 + 2*n
            assert crop(root / "commits" / unit / f"screen-{visible:04}.png") == export
            assert backup("commits", unit, visible) == before
            after = backup("commits", unit, committed)
            value = state(after, 9)
            assert value == [1, 0, 1, 0][n]
            assert [i for i, (a, b) in enumerate(zip(before, after)) if a != b] == [9, 265, 521]
            country_cycle.append(value)
            before = after
        for n in range(4):
            visible, committed = 10 + 2*n, 11 + 2*n
            expected = 0 if unit == "2-powsledr" else [1, 2, 0, 1][n]
            reference = relay if unit == "2-powsledr" else colors[expected]
            assert crop(root / "commits" / unit / f"screen-{visible:04}.png") == reference
            assert backup("commits", unit, visible) == before
            after = backup("commits", unit, committed)
            assert state(after, 8) == expected
            changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
            assert changed == ([8, 264, 520] if state(before, 8) != expected else [])
            ride_cycle.append(expected)
            before = after
        game = unit.split("-", 1)[1]
        assert before == (root / "commits" / unit / "nvram" / game / "backup1").read_bytes()
        verify_run("reload-country-one")
        assert crop(root / "reload-country-one" / unit / "screen-0001.png") == export
        assert state(backup("reload-country-one", unit, 1), 9) == 1
        for name, value in [("red", 1), ("black", 2), ("silver", 0)]:
            folder = "reload-ride-" + name
            verify_run(folder)
            expected = 0 if unit == "2-powsledr" else value
            assert state(backup(folder, unit, 1), 8) == expected
            reference = relay if unit == "2-powsledr" else colors[value]
            assert crop(root / folder / unit / "screen-0001.png") == reference
            assert state(backup(folder, unit, 2), 9) == 0
            assert crop(root / folder / unit / "screen-0002.png") == export
        results[game] = {
            "country": {"stored_cycle": country_cycle, "visible_label": "Export",
                        "base_offset": 9, "encoding": "u8", "copies": 3, "copy_stride": 256,
                        "all_states_committed_and_reloaded": True,
                        "region_meaning": "unverified"},
            "ride_id": {"stored_cycle": ride_cycle, "base_offset": 8,
                        "encoding": "u8", "copies": 3, "copy_stride": 256,
                        "observed_values": [{"id": 256, "label": "Relay"}] if unit == "2-powsledr"
                        else [{"id": v, "label": names[v]} for v in (0, 1, 2)],
                        "all_values_committed_and_reloaded": True,
                        "relay_note": "Relay displays 0x100; its persisted byte is 0, not a u16 0x100" if unit == "2-powsledr" else None},
            "baseline": "Native numeric defaults committed; Country 0 committed before Ride ID acquisition",
        }
    if (root / "country-one-ride-cycle/manifest.json").exists():
        verify_run("country-one-ride-cycle")
        for unit in units:
            cycle = []
            for n in range(4):
                expected = 0 if unit == "2-powsledr" else [1, 2, 0, 1][n]
                before = backup("country-one-ride-cycle", unit, 1 + 2*n)
                after = backup("country-one-ride-cycle", unit, 2 + 2*n)
                assert state(before, 9) == state(after, 9) == 1
                assert state(after, 8) == expected
                reference = relay if unit == "2-powsledr" else colors[expected]
                assert crop(root / "country-one-ride-cycle" / unit / f"screen-{1+2*n:04}.png") == reference
                cycle.append(expected)
            results[unit.split("-", 1)[1]]["ride_id"]["country_one_stored_cycle"] = cycle
    files = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(root.rglob("*")) if p.is_file() and p.name != "observations.json"}
    result = {"status": "all_discrete_states_committed_and_reloaded", "sets": results,
              "files": files, "limits": ["Native region semantics and complete integrity algorithm unverified",
                                           "Whole-image templates and linked gameplay unverified"]}
    (root / "observations.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Discrete campaign passed: Country states 0/1, Main/Slave colors 0/1/2, Relay role; native commits and fresh reloads")


if __name__ == "__main__":
    main()
