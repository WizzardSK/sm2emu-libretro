#!/usr/bin/env python3
"""Verify a Libretro save/load round-trip in an isolated RetroArch process."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import socket
import subprocess
import time

from libretro_nvram_samples import (
    activate_process,
    free_udp_port,
    post_escape_to_pid,
    post_key_to_pid,
    take_screenshot,
    wait_while_alive,
)


def quote(value: Path | str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def wait_for_state(directory: Path, process: subprocess.Popen[bytes]) -> Path:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        states = sorted(directory.rglob("*.state*"), key=lambda path: path.stat().st_mtime_ns)
        if states and states[-1].stat().st_size:
            return states[-1]
        if process.poll() is not None:
            raise RuntimeError(f"RetroArch exited before writing the state ({process.returncode})")
        time.sleep(0.10)
    raise RuntimeError("RetroArch did not write a save state")


def send_command(command_port: int, command: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(f"{command}\n".encode(), ("127.0.0.1", command_port))


def set_paused(command_port: int, paused: bool) -> None:
    """A replay can already be paused at EOF; never toggle blindly."""
    deadline = time.monotonic() + 3.0
    toggled = False
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1.0)
            sock.sendto(b"GET_STATUS\n", ("127.0.0.1", command_port))
            status = sock.recv(4096).decode().split()
        if len(status) < 2 or status[1] not in ("PAUSED", "PLAYING"):
            raise RuntimeError(f"Unexpected frontend status: {status!r}")
        if (status[1] == "PAUSED") == paused:
            return
        if not toggled:
            send_command(command_port, "PAUSE_TOGGLE")
            toggled = True
        time.sleep(0.05)
    raise RuntimeError("RetroArch did not reach the requested pause state")


def crop_game_region(source: Path, destination: Path) -> None:
    """Exclude RetroArch notifications while retaining a large game region."""
    subprocess.run(
        [
            "/usr/bin/sips", "--cropToHeightWidth", "900", "800",
            "--cropOffset", "300", "650", str(source), "--out", str(destination),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def quit_retroarch(process: subprocess.Popen[bytes], command_port: int) -> bool:
    if process.poll() is not None:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(b"QUIT\n", ("127.0.0.1", command_port))
    try:
        process.wait(timeout=8.0)
        return False
    except subprocess.TimeoutExpired:
        try:
            post_escape_to_pid(process.pid)
            time.sleep(1.0)
            if process.poll() is None:
                post_escape_to_pid(process.pid)
            process.wait(timeout=5.0)
            return False
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            process.terminate()
        try:
            process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5.0)
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("retroarch", "core", "system", "rom", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--set-name", required=True)
    parser.add_argument("--boot-wait", type=float, default=38.0)
    parser.add_argument("--advance-wait", type=float, default=3.0)
    parser.add_argument("--software-threading", choices=("asynchronous", "synchronous"),
                        default="asynchronous")
    args = parser.parse_args()

    retroarch = args.retroarch.resolve(strict=True)
    core = args.core.resolve(strict=True)
    system = args.system.resolve(strict=True)
    rom = args.rom.resolve(strict=True)
    replay = args.replay.resolve(strict=True) if args.replay else None
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    for name in ("saves", "states", "screenshots", "config"):
        (output / name).mkdir()

    command_port = free_udp_port()
    core_options = output / "core-options.cfg"
    core_options.write_text(
        'sm2_renderer = "software"\n'
        f'sm2_software_renderer_threading = "{args.software_threading}"\n'
        f'sm2_linked_cabinets_{rom.stem} = "-1"\n'
        f'sm2_automatic_network_{rom.stem} = "-1"\n',
        encoding="utf-8",
    )
    config_values = {
        "config_save_on_exit": "false",
        "log_to_file": "false",
        "user_language": "0",
        "history_list_enable": "false",
        "content_runtime_log": "false",
        "content_runtime_log_aggregate": "false",
        "cheevos_enable": "false",
        "cheevos_hardcore_mode_enable": "false",
        "system_directory": system,
        "savefile_directory": output / "saves",
        "savestate_directory": output / "states",
        "screenshot_directory": output / "screenshots",
        "core_options_path": core_options,
        "global_core_options": "true",
        "network_cmd_enable": "true",
        "network_cmd_port": str(command_port),
        "video_driver": "gl",
        "audio_driver": "coreaudio",
        "input_driver": "cocoa",
        "video_fullscreen": "false",
        "video_windowed_fullscreen": "false",
        "video_scale": "2",
        "video_vsync": "false",
        "audio_sync": "true",
        "audio_enable": "true",
        "pause_nonactive": "false",
        "savestate_auto_save": "false",
        "savestate_auto_load": "false",
        "savestate_auto_index": "false",
        "savestate_file_compression": "false",
        "savestate_thumbnail_enable": "false",
        "state_slot": "0",
        "input_pause_toggle": "p",
        "input_save_state": "f2",
        "input_load_state": "f4",
        "input_frame_advance": "k",
        "video_shader_enable": "false",
        "video_threaded": "false",
        "auto_overrides_enable": "false",
        "auto_remaps_enable": "false",
    }
    config = output / "retroarch.cfg"
    config.write_text(
        "".join(f'{key} = "{quote(value)}"\n' for key, value in config_values.items()),
        encoding="utf-8",
    )
    command = [str(retroarch), "-v", "-c", str(config), "-L", str(core)]
    if replay:
        local_replay = output / "input.replay"
        shutil.copy2(replay, local_replay)
        command.extend(["-P", str(local_replay)])
    command.append(str(rom))
    (output / "command.json").write_text(json.dumps(command, indent=2) + "\n")

    forced = False
    with (output / "run.log").open("wb") as log:
        process = subprocess.Popen(command, cwd=output, stdout=log, stderr=subprocess.STDOUT)
        try:
            activate_process(process)
            wait_while_alive(process, args.boot_wait)
            set_paused(command_port, True)
            wait_while_alive(process, 1.0)
            send_command(command_port, "SAVE_STATE")
            state = wait_for_state(output / "states", process)
            wait_while_alive(process, 2.5)
            # Original Model 2 rebuilds geometry every other frame. Three
            # steps also cover the asynchronous renderer's one-frame delay.
            for _ in range(3):
                post_key_to_pid(process.pid, 40, "Frame Advance")
                wait_while_alive(process, 0.5)
            saved = take_screenshot(process, output, command_port, "saved")

            set_paused(command_port, False)
            wait_while_alive(process, args.advance_wait)
            set_paused(command_port, True)
            wait_while_alive(process, 1.0)
            advanced = take_screenshot(process, output, command_port, "advanced")

            # Screenshot file creation precedes task completion in RetroArch.
            # Let its blocking task leave the queue before requesting a load.
            wait_while_alive(process, 1.0)

            # Explicit slot command bypasses transient hotkey delivery.
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(3.0)
                sock.sendto(b"LOAD_STATE_SLOT 0\n", ("127.0.0.1", command_port))
                reply = sock.recv(1024).decode().strip()
                if reply != "LOAD_STATE_SLOT 0":
                    raise RuntimeError(f"Unexpected load reply: {reply!r}")
            wait_while_alive(process, 2.0)
            # Match the same geometry/presentation warm-up as the reference.
            for _ in range(3):
                post_key_to_pid(process.pid, 40, "Frame Advance")
                wait_while_alive(process, 0.5)
            restored = take_screenshot(process, output, command_port, "restored")
            set_paused(command_port, False)
            wait_while_alive(process, 0.5)
            resumed = take_screenshot(process, output, command_port, "resumed")
        finally:
            forced = quit_retroarch(process, command_port)

    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    saved_hash = digest(saved)
    advanced_hash = digest(advanced)
    restored_hash = digest(restored)
    saved_crop = output / "screenshots" / "saved-game-region.png"
    restored_crop = output / "screenshots" / "restored-game-region.png"
    advanced_crop = output / "screenshots" / "advanced-game-region.png"
    resumed_crop = output / "screenshots" / "resumed-game-region.png"
    crop_game_region(saved, saved_crop)
    crop_game_region(restored, restored_crop)
    crop_game_region(advanced, advanced_crop)
    crop_game_region(resumed, resumed_crop)
    saved_game_hash = digest(saved_crop)
    restored_game_hash = digest(restored_crop)
    log_text = (output / "run.log").read_text(encoding="utf-8", errors="replace")
    result = {
        "set_name": args.set_name,
        "software_threading": args.software_threading,
        "pause_state_verified": True,
        "state": str(state),
        "state_size": state.stat().st_size,
        "saved_screenshot": str(saved),
        "advanced_screenshot": str(advanced),
        "restored_screenshot": str(restored),
        "saved_sha256": saved_hash,
        "advanced_sha256": advanced_hash,
        "restored_sha256": restored_hash,
        "saved_game_region_sha256": saved_game_hash,
        "restored_game_region_sha256": restored_game_hash,
        "advanced_changed": digest(advanced_crop) != saved_game_hash,
        "resumed_changed": digest(resumed_crop) != restored_game_hash,
        "resumed_screenshot": str(resumed),
        "comparison_frame_steps": 3,
        "restored_game_region_exactly": restored_game_hash == saved_game_hash,
        "save_log_message": (
            "Salvataggio dello stato" in log_text or "Saving state" in log_text
        ),
        "load_log_message": (
            "Caricamento dello stato" in log_text or "Loading state" in log_text
        ),
        "exit_code": process.returncode,
        "forced_kill": forced,
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    if not result["save_log_message"] or not result["load_log_message"]:
        raise RuntimeError("RetroArch did not confirm both Save State and Load State")
    if not result["advanced_changed"]:
        raise RuntimeError("The game image did not advance after saving")
    if not result["restored_game_region_exactly"]:
        raise RuntimeError("The loaded state did not restore the saved video frame exactly")
    if not result["resumed_changed"]:
        raise RuntimeError("The game image did not advance after loading")
    if process.returncode != 0 or forced:
        raise RuntimeError("RetroArch did not close cleanly")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
