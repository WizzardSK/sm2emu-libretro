#!/usr/bin/env python3
"""Launch interactive linked SM2 cabinets using the established RetroArch runner.

A single --game name starts one instance; --cabinets N repeats that ROM.
A comma-separated list selects each
instance's ROM. Optional :ANS:GAMEPAD fields select ANS (0, 1, 2... or relay/r) and a
one-based pad ID. Missing fields allocate IDs; an explicitly empty pad field
assigns no gamepad. Power Sled ignores
--relay; its Main/Slave/Relay triplet gets the dedicated layout. Saves and configuration belong
to the selected session directory; global RetroArch files are not modified.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("linked_runner", ROOT / "scripts/test-retroarch-netpacket.py")
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


def game_plan(selection: str, cabinets: int | None, relay: bool):
    entries = []
    for token in selection.split(","):
        parts = token.strip().split(":")
        if len(parts) not in (1, 2, 3) or not re.fullmatch(r"[A-Za-z0-9_-]+", parts[0]):
            raise ValueError("--game requires name[:ANS[:GAMEPAD]] entries")
        preset = (parts[1] or None) if len(parts) >= 2 else None
        if preset == "r":
            preset = "relay"
        if preset is not None and preset not in {"0", "relay", *map(str, range(1, 10))}:
            raise ValueError("ANS uses 0, 1..9, relay or r")
        pad = "auto" if len(parts) < 3 else parts[2] or None
        if pad not in (None, "auto"):
            if pad not in set(map(str, range(1, 17))):
                raise ValueError("gamepad IDs use 1..16; an empty field assigns no gamepad")
            pad = int(pad)
        entries.append((parts[0], preset, pad))
    if len(entries) == 1:
        entries *= cabinets or 1
    elif cabinets is not None and cabinets != len(entries):
        raise ValueError("--cabinets must match the number of listed games")
    if not 1 <= len(entries) <= 9:
        raise ValueError("provide 1..9 instances")
    if relay and not all(game in {"powsledm", "powsled", "powsledr"} for game, _, _ in entries) and entries[-1][1] is None:
        game, _, pad = entries[-1]
        entries[-1] = (game, "relay", pad)
    used_ans = {preset for _, preset, _ in entries if preset is not None}
    used_pads = [pad for _, _, pad in entries if isinstance(pad, int)]
    if len(set(used_pads)) != len(used_pads):
        raise ValueError("assign distinct gamepad IDs to instances")
    used_pads = set(used_pads)
    resolved = []
    for game, preset, pad in entries:
        if preset is None:
            preset = next(str(value) for value in range(1, 10) if str(value) not in used_ans)
            used_ans.add(preset)
        if pad == "auto":
            pad = next(value for value in range(1, 17) if value not in used_pads)
            used_pads.add(pad)
        resolved.append((game, preset, pad))
    entries = resolved
    sled = {"powsledm", "powsled", "powsledr"}
    power_family = all(game in sled for game, _, _ in entries)
    displayed = [game for game, _, _ in entries]
    power = (power_family and len(entries) >= 3
             and displayed.count("powsledm") == 1 and displayed.count("powsledr") == 1)
    order = ([displayed.index("powsledm"),
              *(index for index, game in enumerate(displayed) if game == "powsled"),
              displayed.index("powsledr")] if power else list(range(len(entries))))
    # Only arrange the known Power Sled ring; never validate game compatibility.
    include_relay = not power_family and (relay or entries[-1][1] == "relay")
    return entries, order, power, include_relay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True,
                        help="name[:ANS[:GAMEPAD]],...; pad IDs start at 1; empty pad field disables assignment")
    parser.add_argument("--cabinets", type=int, choices=range(1, 10), help="Repeat a single ROM N times (default 1); with a list, N must match its length")
    parser.add_argument("--relay", action="store_true", help="Use a generic Relay where supported; ignored for Power Sled")
    parser.add_argument("--rom-dir", type=Path, default=Path("/Volumes/MacBook External Drive/Retro/_Media/Sega - _Arcade (Model 2)/roms"))
    parser.add_argument("--retroarch", type=Path, default=Path.home() / "Retro/Apps/RetroArch/Nightly/RetroArch (ARM).app/Contents/MacOS/RetroArch")
    parser.add_argument("--core", type=Path, default=Path.home() / "Library/Application Support/RetroArch/cores/sm2_libretro.dylib")
    parser.add_argument("--base-config", type=Path, default=Path.home() / "Library/Application Support/RetroArch/config/retroarch.cfg")
    parser.add_argument("--system-assets", type=Path, default=ROOT / "build-libretro-gpu/libretro/system/sm2-emu")
    parser.add_argument("--session", type=Path, help="New session directory, or an existing launcher session to resume")
    parser.add_argument("--desktop-size", help="Override usable desktop area as WIDTHxHEIGHT; otherwise detect macOS monitor")
    parser.add_argument("--port", type=int, default=55435)
    parser.add_argument("--dry-run", action="store_true", help="Prepare configuration without starting RetroArch")
    parser.add_argument("--seconds", type=float, help="Bounded launch instead of interactive play")
    parser.add_argument("--capture-screenshots", action="store_true")
    args = parser.parse_args()
    try:
        entries, order, power, include_relay = game_plan(args.game, args.cabinets, args.relay)
    except ValueError as error:
        parser.error(str(error))
    displayed = [game for game, _, _ in entries]
    count = len(entries)
    native_games = [entries[index][0] for index in order]
    native_presets = [entries[index][1] for index in order]
    roles = ["host" if index == 0 else
             "_relay" if (power or include_relay or native_games[-1] == "powsledr") and index == count - 1 else
             f"client{index}" for index in range(count)]
    host = native_games[0]
    controllers = [pad for _, _, pad in entries]
    if args.seconds is not None and args.seconds <= 0:
        parser.error("--seconds must be positive")
    session_name = host if power or len(set(displayed)) == 1 else "-".join(displayed)
    session = (args.session.expanduser().resolve() if args.session else
               ROOT / "build-libretro-gpu/linked-cabinets" / f"{session_name}-{count}")
    identity = {"host_set": host, "displayed_games": displayed}
    marker = session / "launcher.json"
    if session.exists() and not marker.exists() and any(session.iterdir()):
        parser.error("existing --session must be owned by this launcher")
    session.mkdir(parents=True, exist_ok=True)
    if marker.exists() and json.loads(marker.read_text()) != identity:
        parser.error("session game/topology differs; use a new directory")
    marker.write_text(json.dumps(identity, indent=2) + "\n")
    attempts = session / "runs"
    attempts.mkdir(exist_ok=True)
    number = max((int(path.name) for path in attempts.iterdir() if path.name.isdigit()), default=0) + 1
    run = attempts / f"{number:04d}"
    run.mkdir(exist_ok=False)
    previous = sorted(path for path in attempts.iterdir() if path != run and (path / "cabinets/result.json").exists()
                      and json.loads((path / "cabinets/result.json").read_text()).get("status") == "ok")
    native_pads = [controllers[index] for index in order]
    cmd = [sys.executable, str(ROOT / "scripts/test-retroarch-netpacket.py"),
           "--retroarch", str(args.retroarch), "--core", str(args.core),
           "--base-config", str(args.base_config), "--system-assets", str(args.system_assets),
           "--rom", str(args.rom_dir / f"{host}.zip"), "--set-name", host,
           "--instance-games", ",".join(native_games),
           "--instance-roles", ",".join(roles),
           "--cabinets", str(count), "--automatic-network", "--play-audio",
           "--controller-indices", ",".join("none" if pad is None else str(pad - 1) for pad in native_pads),
           "--window-layout", "power-sled" if power and count == 3 else "side-by-side",
           "--window-columns", str(count - 1 if count > 1 and roles[-1] == "_relay" else count),
           "--fit-windows",
           "--port", str(args.port), "--output", str(run / "cabinets")]
    if args.desktop_size:
        cmd += ["--desktop-size", args.desktop_size]
    if power:
        cmd += ["--relay-rom", str(args.rom_dir / "powsledr.zip"),
                "--slave-rom", str(args.rom_dir / "powsled.zip")]
    elif "vonr" in native_games:
        cmd += ["--relay-rom", str(args.rom_dir / "vonr.zip")]
    elif include_relay:
        cmd += ["--include-relay"]
    options = {}
    if previous:
        cmd += ["--baseline-run", str(previous[-1] / "cabinets")]
    for index, (game, preset) in enumerate(zip(native_games, native_presets)):
        role = roles[index]
        saved = {}
        if previous:
            path = runner.baseline_directory(previous[-1] / "cabinets", role, game, index) / "config/core-options.cfg"
            saved = dict(re.findall(r'^([^\s=]+) = "([^"\n]*)"$', path.read_text(), re.M))
            key = f"sm2_automatic_network_{game}"
            retained_color = saved.get(key) if power else None
            saved = {key: value for key, value in saved.items()
                     if not key.startswith(("sm2_automatic_network_", "sm2_linked_cabinets_"))}
            if retained_color in {"0", "1", "2", "3", "4", "relay"}:
                saved[key] = retained_color
        saved[f"sm2_linked_cabinets_{game}"] = "disabled" if count == 1 else str(count)
        saved["sm2_nvram_settings"] = "enabled"
        if preset is not None:
            saved[f"sm2_automatic_network_{game}"] = preset
        options[role] = saved
    path = run / "options.json"
    path.write_text(json.dumps(options, indent=2) + "\n")
    cmd += ["--core-options-override", str(path), "--settle", str(args.seconds or 10)]
    if args.seconds is None:
        cmd += ["--interactive"]
    if args.dry_run:
        cmd += ["--dry-run"]
    if args.capture_screenshots:
        cmd += ["--capture-screenshots"]
    (run / "command.json").write_text(json.dumps(cmd, indent=2) + "\n")
    print("Session:", session, flush=True)
    for game, preset, pad in entries:
        print(f"  {game}: ANS {preset}, gamepad {pad if pad is not None else 'none'}", flush=True)
    process = subprocess.Popen(cmd)
    try:
        return process.wait()
    except KeyboardInterrupt:
        process.wait(timeout=40)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
