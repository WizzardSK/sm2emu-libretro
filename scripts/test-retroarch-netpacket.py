#!/usr/bin/env python3
"""Exercise SM2 linked cabinets through isolated RetroArch instances.

The lifecycle follows the established NVRAM/smoke-test runners: every process
is recorded immediately, all paths are isolated, and cleanup always waits for
termination before returning.  The script refuses to start while another copy
of the selected RetroArch executable is running, unless the explicit isolated
coexistence flag is supplied. Cleanup owns only the instances it starts.
"""

from __future__ import annotations

import argparse
import atexit
import hashlib
import tomllib
import binascii
import json
import plistlib
import re
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path

from libretro_nvram_samples import (
    activate_process,
    expand_actions,
    validate_close,
    action_label,
    find_saves,
    free_udp_port,
    position_process_window,
    post_escape_to_pid,
    take_screenshot,
    send_button_state,
    wait_while_alive,
)


PREFERENCES_DOMAIN = "com.libretro.dist.RetroArch"
IGNORE_STATE_KEY = "ApplePersistenceIgnoreState"
WINDOW_WIDTH = 496
WINDOW_HEIGHT = 384
# RetroArch adds the native macOS frame around the configured content area.
WINDOW_FRAME_WIDTH = 512
WINDOW_FRAME_HEIGHT = 412
WINDOW_GAP = 16
WINDOW_ORIGIN_X = 24
WINDOW_ORIGIN_Y = 40


@dataclass(frozen=True)
class GameSpec:
    max_cabinets: int
    nvram_game: str
    nvram_scheme: str


GAME_SPECS = {
    "powsledm": GameSpec(5, "powsledm", "power_sled"),
    "powsledr": GameSpec(5, "powsledr", "power_sled"),
    "powsled": GameSpec(5, "powsled", "power_sled"),
    "daytona": GameSpec(8, "daytona", "daytona"),
    "daytonas": GameSpec(8, "daytonas", "daytona"),
    "daytonagtx": GameSpec(8, "daytonagtx", "daytona"),
    "daytonase": GameSpec(8, "daytona", "daytona"),
    "daytonam": GameSpec(8, "daytona", "daytona"),
    "stcc": GameSpec(9, "stcc", "car"),
    "stcca": GameSpec(9, "stcca", "car"),
    "stccb": GameSpec(9, "stccb", "car"),
    "stcco": GameSpec(9, "stcco", "car"),
    "srallyc": GameSpec(5, "srallyc", "car"),
    "srallycb": GameSpec(5, "srallyc", "car"),
    "srallycc": GameSpec(5, "srallyc", "car"),
    "indy500": GameSpec(8, "indy500", "role_id"),
    "indy500d": GameSpec(8, "indy500d", "role_id"),
    "indy500to": GameSpec(8, "indy500", "role_id"),
    "motoraid": GameSpec(5, "motoraid", "role_id"),
    "motoraiddx": GameSpec(5, "motoraiddx", "role_id"),
    "waverunr": GameSpec(4, "waverunr", "role_id"),
    "skisuprg": GameSpec(4, "skisuprg", "role_id"),
    "sgt24h": GameSpec(4, "sgt24h", "sgt24h"),
    "overrev": GameSpec(4, "overrev", "overrev"),
    "overrevb": GameSpec(4, "overrev", "overrev"),
    "overrevba": GameSpec(4, "overrev", "overrev"),
    "manxtt": GameSpec(3, "manxtt", "link_role"),
    "manxttc": GameSpec(3, "manxtt", "link_role"),
    "von": GameSpec(3, "von", "network_attribute"),
    "vonj": GameSpec(3, "von", "network_attribute"),
    "vonu": GameSpec(3, "von", "network_attribute"),
}

VIRTUAL_ON_TWIN_SETS = {"von", "vonj", "vonu"}
VIRTUAL_ON_RELAY_SPEC = GameSpec(3, "von", "relay_program")
OPTIONAL_RELAY_SETS = {
    "stcc", "stcca", "stccb", "stcco",
    "srallyc", "srallycb", "srallycc",
    "motoraid", "motoraiddx",
}


def game_spec(set_name: str) -> GameSpec:
    if set_name == "vonr":
        return VIRTUAL_ON_RELAY_SPEC
    return GAME_SPECS.get(set_name, GameSpec(9, set_name, "unmanaged"))


@dataclass
class InstanceResult:
    role: str
    pid: int
    exit_code: int | None = None
    forced_kill: bool = False
    roster_ready: bool = False
    native_link_ready: bool = False
    log: str = ""
    screenshot: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retroarch", type=Path, required=True)
    parser.add_argument("--core", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument(
        "--relay-rom", type=Path,
        help="Dedicated vonr or powsledr Relay ROM",
    )
    parser.add_argument("--service-menu", action="store_true",
                        help="Power Sled only: verify Service Menu and Game Assignments without changing settings")
    parser.add_argument("--slave-rom", type=Path, help="Power Sled Slave ROM (powsled.zip)")
    parser.add_argument("--instance-games", help="Per-instance ROM set names in native participant order")
    parser.add_argument("--instance-roles", help="Per-participant session folder names; defaults to host,client1,...")
    parser.add_argument(
        "--include-relay", action="store_true",
        help="Use the final cabinet as Relay, or Live for Motor Raid",
    )
    parser.add_argument(
        "--base-config", type=Path,
        default=Path("~/Library/Application Support/RetroArch/config/retroarch.cfg"),
        help="RetroArch configuration copied before isolated overrides",
    )
    parser.add_argument(
        "--system-assets", type=Path, required=True,
        help="Directory containing games.xml and the remaining SM2 system files",
    )
    parser.add_argument(
        "--set-name", default="daytona",
        help="First instance ROM set; reviewed metadata supplies automatic presets where available",
    )
    parser.add_argument("--cabinets", type=int, choices=range(1, 10), default=3)
    parser.add_argument("--allow-existing-retroarch", action="store_true",
                        help="Run isolated peers alongside an existing RetroArch process; cleanup owns only launched PIDs")
    parser.add_argument(
        "--automatic-network", action="store_true",
        help="Use the native Auto Network Role Settings presets instead of manual NVRAM selectors",
    )
    parser.add_argument(
        "--instance-indices",
        help=(
            "Comma-separated zero-based cabinet indices launched on this host; "
            "default launches every cabinet"
        ),
    )
    parser.add_argument(
        "--connect-host", default="127.0.0.1",
        help="Netpacket host used by client instances (default: 127.0.0.1)",
    )
    parser.add_argument("--port", type=int, default=55435)
    parser.add_argument("--startup-wait", type=float, default=5.0)
    parser.add_argument("--settle", type=float, default=10.0)
    parser.add_argument(
        "--window-layout", choices=("side-by-side", "cascade", "power-sled"),
        default="side-by-side",
        help="Arrange isolated RetroArch windows side by side or in a cascade",
    )
    parser.add_argument("--fit-windows", action="store_true",
                        help="Reduce equal-sized windows to fit the usable macOS desktop")
    parser.add_argument("--desktop-size", help="Override usable desktop dimensions as WIDTHxHEIGHT (logical points)")
    parser.add_argument(
        "--window-columns", type=int, default=2,
        help="Number of columns used by the side-by-side layout (default: 2)",
    )
    parser.add_argument(
        "--output", type=Path,
        help="Persistent result directory; default is a unique temporary directory",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Create and validate the isolated environments without launching RetroArch",
    )
    parser.add_argument(
        "--capture-screenshots", action="store_true",
        help="Capture one frontend screenshot from every local instance",
    )
    parser.add_argument("--operator-recipe", type=Path, help="Power Sled linked operator TOML recipe")
    parser.add_argument("--sample", help="Run one recipe suffix; omit to execute/resume the complete campaign")
    parser.add_argument("--baseline-run", type=Path, help="Prior linked RetroArch run supplying each program's own SRM")
    parser.add_argument("--core-options-override", type=Path,
                        help="JSON map of set names to Core Option values for isolated verification")
    parser.add_argument("--native-nvram-baseline", type=Path,
                        help="Role directories containing native .nv/.eeprom samples for precedence verification")
    parser.add_argument("--menu-frame-samples", type=int, default=1,
                        help="Capture repeated unchanged Power Sled menu frames (1-20; requires --service-menu)")
    parser.add_argument(
        "--input-replay", type=Path,
        help="Optional RetroArch input replay applied to every local instance",
    )
    parser.add_argument("--input-replay-map", type=Path,
                        help="JSON role-to-replay-path overrides for individual local instances")
    parser.add_argument("--record-audio", action="store_true",
                        help="Record each isolated instance's PCM through RetroArch's WAV driver")
    parser.add_argument("--screenshot-samples", type=int, default=1,
                        help="Number of linked observation rounds (1-20; requires --capture-screenshots)")
    parser.add_argument("--screenshot-gap", type=float, default=5.0,
                        help="Seconds between observation rounds (0-60)")
    parser.add_argument("--network-exercise",choices=("resume-restart","stall","reconnect","options"),
                        help="Bounded menu/reset, process-stall, peer-reconnect or interactive Core Options verification")
    parser.add_argument("--interactive", action="store_true",
                        help="Keep the cabinets running until one closes or Ctrl+C; no scripted inputs")
    parser.add_argument("--controller-indices",
                        help="Distinct zero-based pad indices or none in native instance order; macOS resolves sorted physical HID names once")
    parser.add_argument("--play-audio", action="store_true",
                        help="Enable native audio without recording PCM")
    return parser.parse_args()


def quote_config(value: Path | str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def local_instance_indices(value: str | None, cabinets: int) -> list[int]:
    if value is None:
        return list(range(cabinets))
    try:
        indices = [int(item.strip()) for item in value.split(",")]
    except ValueError as error:
        raise RuntimeError("--instance-indices must contain integers") from error
    if not indices or len(set(indices)) != len(indices):
        raise RuntimeError("--instance-indices must contain distinct cabinet indices")
    if any(index < 0 or index >= cabinets for index in indices):
        raise RuntimeError(
            f"--instance-indices must be between 0 and {cabinets - 1}"
        )
    return indices


def usable_desktop(size: str | None) -> tuple[int, int, int, int]:
    if size is not None:
        match = re.fullmatch(r"([1-9][0-9]*)x([1-9][0-9]*)", size)
        if not match:
            raise RuntimeError("--desktop-size requires positive WIDTHxHEIGHT dimensions")
        return 0, 0, int(match[1]), int(match[2])
    if sys.platform != "darwin":
        raise RuntimeError("automatic desktop sizing currently requires macOS; use --desktop-size")
    script = ('ObjC.import("AppKit"); const screen = $.NSScreen.mainScreen; '
              'const primary = $.NSScreen.screens.objectAtIndex(0).frame; const visible = screen.visibleFrame; '
              'JSON.stringify([visible.origin.x, primary.size.height - visible.origin.y '
              '- visible.size.height, visible.size.width, visible.size.height]);')
    return tuple(map(int, json.loads(subprocess.check_output(
        ["/usr/bin/osascript", "-l", "JavaScript", "-e", script], text=True))))


def fitted_window_size(count: int, columns: int, width: int, height: int) -> tuple[int, int]:
    columns = min(columns, count)
    rows = (count + columns - 1) // columns
    # Preserve native content proportions; reserve measured frame overhead,
    # inter-window gaps and a margin on all sides. Never enlarge beyond 1x.
    available_width = width - 48 - (columns - 1) * WINDOW_GAP - columns * 16
    available_height = height - 48 - (rows - 1) * WINDOW_GAP - rows * 28
    scale = min(1.0, available_width / (columns * 496), available_height / (rows * 384))
    if scale <= 0:
        raise RuntimeError("desktop area is too small for the requested window layout")
    return max(1, int(496 * scale)), max(1, int(384 * scale))


def window_position(index: int, layout: str, columns: int) -> tuple[int, int]:
    if layout == "cascade":
        return WINDOW_ORIGIN_X + index * 60, WINDOW_ORIGIN_Y + index * 40
    if layout == "power-sled":
        index = (0, 2, 1)[index]  # Native Main/Relay/Slave -> visible Main/Slave/Relay.
        columns = 2
    column = index % columns
    row = index // columns
    return (
        WINDOW_ORIGIN_X + column * (WINDOW_FRAME_WIDTH + WINDOW_GAP),
        WINDOW_ORIGIN_Y + row * (WINDOW_FRAME_HEIGHT + WINDOW_GAP),
    )


def fit_process_window(process: subprocess.Popen[bytes], x: int, y: int,
                       width: int, height: int, *, apply: bool = True) -> dict[str, int] | None:
    """Apply and read back the actual outer frame, owned by this process only."""
    commands = (f'  set size of window 1 to {{{width}, {height}}}\n'
                f'  set position of window 1 to {{{x}, {y}}}\n') if apply else ""
    script = (
        'tell application "System Events" to tell first application process '
        f'whose unix id is {process.pid}\n'
        + commands +
        '  return (position of window 1) & (size of window 1)\n'
        'end tell'
    )
    for attempt in range(3):
        if process.poll() is not None:
            if not apply:
                return None
            raise RuntimeError("RetroArch exited before its window could be resized")
        try:
            raw = subprocess.check_output(
                ["/usr/bin/osascript", "-e", script], text=True, timeout=5).strip()
            values = [int(value.strip()) for value in raw.split(",")]
        except (ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            if attempt < 2:
                time.sleep(0.1)
                continue
            if not apply:
                return None  # A closed/hidden window is no longer measurable.
            raise RuntimeError("macOS could not read the new RetroArch window frame") from None
        if len(values) != 4 or any(abs(actual - expected) > 1
                                  for actual, expected in zip(values, (x, y, width, height))):
            raise RuntimeError(f"RetroArch window frame differs from requested {(x, y, width, height)}: {values}")
        return dict(zip(("x", "y", "frame_width", "frame_height"), values))


def process_rows() -> list[tuple[int, str]]:
    completed = subprocess.run(
        ["/bin/ps", "-ax", "-o", "pid=,command="],
        check=True,
        capture_output=True,
        text=True,
    )
    rows: list[tuple[int, str]] = []
    for line in completed.stdout.splitlines():
        fields = line.strip().split(maxsplit=1)
        if len(fields) == 2 and fields[0].isdigit():
            rows.append((int(fields[0]), fields[1]))
    return rows


def retroarch_processes(executable: Path) -> list[tuple[int, str]]:
    prefix = str(executable)
    return [(pid, command) for pid, command in process_rows()
            if command == prefix or command.startswith(prefix + " ")]


def port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def read_ignore_state() -> bool | None:
    if sys.platform != "darwin":
        return None
    completed = subprocess.run(
        ["/usr/bin/defaults", "read", PREFERENCES_DOMAIN, IGNORE_STATE_KEY],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip().lower()
    if value in {"1", "true", "yes"}:
        return True
    if value in {"0", "false", "no"}:
        return False
    raise RuntimeError(f"unsupported {IGNORE_STATE_KEY} preference: {value!r}")


def write_ignore_state(value: bool | None) -> None:
    if sys.platform != "darwin":
        return
    if value is None:
        subprocess.run(
            ["/usr/bin/defaults", "delete", PREFERENCES_DOMAIN, IGNORE_STATE_KEY],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return
    subprocess.run(
        ["/usr/bin/defaults", "write", PREFERENCES_DOMAIN, IGNORE_STATE_KEY,
         "-bool", "true" if value else "false"],
        check=True,
    )


def mac_controller_names(indices: list[int | None]) -> list[str | None]:
    """Resolve the CLI's common pad order before any RetroArch process starts."""
    if all(index is None for index in indices):
        return [None] * len(indices)
    devices = plistlib.loads(subprocess.check_output(
        ["/usr/sbin/ioreg", "-a", "-r", "-c", "IOHIDDevice"]))
    names = sorted((item["Product"] for item in devices
                    if item.get("PrimaryUsagePage") == 1
                    and item.get("PrimaryUsage") in (4, 5)
                    and item.get("Transport")
                    and isinstance(item.get("Product"), str)), key=str.casefold)
    selected = []
    for index in indices:
        if index is None:
            selected.append(None)
            continue
        if index >= len(names):
            raise RuntimeError(f"controller index {index} is unavailable; connected pads: {names}")
        name = names[index]
        if names.count(name) != 1:
            raise RuntimeError(f"controller name {name!r} is ambiguous; give the pads distinct macOS names")
        if any(character in name for character in '\"\\\n\r'):
            raise RuntimeError("controller name cannot be represented in a RetroArch reservation")
        selected.append(name)
    return selected


def write_controller_config(config: Path, index: int | None, name: str | None) -> None:
    with config.open("a") as file:
        # Keep a permutation: RetroArch's reservation swaps assume unique indices.
        indices = (list(range(16)) if index is None else
                   [index] + [value for value in range(16) if value != index])
        for player, pad in enumerate(indices, 1):
            reserved = name if player == 1 and name is not None else ""
            file.write(f'input_player{player}_joypad_index = "{pad}"\n')
            file.write(f'input_player{player}_device_reservation_type = "{2 if reserved else 0}"\n')
            file.write(f'input_player{player}_reserved_device = "{reserved}"\n')
        if index is None:
            # Keep valid indices: -1 crashes this frontend's autoconfiguration.
            # Disable the Libretro port instead of relying on a null joypad
            # driver, which this frontend silently replaces with SDL.
            file.write('input_autodetect_enable = "false"\n')
        if name is not None:
            file.write('input_joypad_driver = "hid"\n')
            file.write('input_autodetect_enable = "true"\n')
        file.write(f'input_libretro_device_p1 = "{0 if index is None else 1}"\n')
        for player in range(2, 9):
            file.write(f'input_libretro_device_p{player} = "0"\n')


def write_config(root: Path, assets: Path, base_config: Path, port: int,
                 command_port: int, cabinets: int, window_x: int,
                 window_y: int, remote_port: int | None = None) -> list[str]:
    for directory in (
        "system/sm2-emu", "saves", "states", "logs", "config", "remaps",
        "screenshots",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)
    for asset in assets.iterdir():
        if asset.is_file():
            shutil.copy2(asset, root / "system" / "sm2-emu" / asset.name)

    values = {
        "config_save_on_exit": "false",
        "system_directory": root / "system",
        "savefile_directory": root / "saves",
        "savestate_directory": root / "states",
        "log_dir": root / "logs",
        "log_to_file": "false",
        "log_to_file_timestamp": "false",
        "log_verbosity": "true",
        "core_options_path": root / "config" / "core-options.cfg",
        "global_core_options": "true",
        "game_specific_options": "false",
        "input_remapping_directory": root / "remaps",
        "input_exit_emulator": "escape",
        "quit_press_twice": "false",
        "auto_overrides_enable": "false",
        "auto_remaps_enable": "false",
        "rgui_config_directory": root / "config",
        "content_history_enable": "false",
        "history_list_enable": "false",
        "content_history_path": root / "config" / "content_history.lpl",
        "content_favorites_path": root / "config" / "content_favorites.lpl",
        "sort_savefiles_enable": "false",
        "sort_savefiles_by_content_enable": "false",
        "savestate_auto_load": "false",
        "savestate_auto_save": "false",
        "pause_nonactive": "false",
        "video_driver": "gl",
        "video_fullscreen": "false",
        "video_windowed_fullscreen": "false",
        "video_window_custom_size_enable": "true",
        "video_windowed_position_width": str(WINDOW_WIDTH),
        "video_windowed_position_height": str(WINDOW_HEIGHT),
        "video_windowed_position_x": str(window_x),
        "video_windowed_position_y": str(window_y),
        "video_scale": "1.000000",
        "video_window_save_positions": "false",
        "video_shader_enable": "false",
        "screenshot_directory": root / "screenshots",
        "notification_show_screenshot": "false",
        "menu_enable_widgets": "false",
        "video_font_enable": "false",
        "audio_driver": "null",
        "audio_enable": "false",
        "microphone_driver": "null",
        "microphone_enable": "false",
        "camera_allow": "false",
        "location_allow": "false",
        "ui_companion_enable": "false",
        "netplay_ip_port": str(port),
        "netplay_max_connections": str(cabinets),
        "netplay_public_announce": "false",
        "netplay_use_mitm_server": "false",
        "netplay_nat_traversal": "false",
        "netplay_check_frames": "0",
        "netplay_nickname": root.name,
        "network_cmd_enable": "true",
        "network_cmd_port": str(command_port),
    }
    if cabinets == 1:
        values["netplay_enable"] = "false"
    if remote_port is not None:
        values.update(network_remote_enable="true",
                      network_remote_enable_user_p1="true",
                      network_remote_base_port=str(remote_port))
    overrides = root / "netpacket-overrides.cfg"
    overrides.write_text(
        "".join(f'{key} = "{quote_config(value)}"\n' for key, value in values.items()),
        encoding="utf-8",
    )
    base_copy = root / "base-retroarch.cfg"
    shutil.copy2(base_config, base_copy)
    return ["-c", str(base_copy), f"--appendconfig={overrides}"]


def write_options(
    root: Path,
    set_name: str,
    cabinets: int,
    index: int,
    include_relay: bool,
    automatic_network: bool,
) -> None:
    spec = game_spec(set_name)
    options = {
        f"sm2_linked_cabinets_{set_name}": str(cabinets),
        "sm2_renderer": "software",
        "sm2_initial_nvram_setup": "enabled",
        "sm2_nvram_settings": "disabled" if automatic_network else "enabled",
    }
    if cabinets == 1:
        options[f"sm2_linked_cabinets_{set_name}"] = "-1"
        options[f"sm2_automatic_network_{set_name}"] = (
            "r" if set_name in {"powsledr", "vonr"} else "1" if spec.nvram_scheme == "power_sled" else "0")
        path = root / "config" / "core-options.cfg"
        path.write_text(
            "".join(f"{key} = {json.dumps(value)}\n" for key, value in options.items()),
            encoding="utf-8",
        )
        return
    if spec.nvram_scheme == "power_sled":
        options["sm2_initial_nvram_setup"] = "enabled" if automatic_network else "disabled"
        options["sm2_nvram_settings"] = "disabled"
    if set_name in {"powsledr", "vonr"}:
        options[f"sm2_automatic_network_{set_name}"] = "r"
    elif not automatic_network:
        options[f"sm2_automatic_network_{set_name}"] = "-1"
    if spec.nvram_scheme == "power_sled":
        # Programs fix roles. Only reviewed Main/Slave Ride color is managed.
        if automatic_network and set_name != "powsledr":
            options[f"sm2_automatic_network_{set_name}"] = "2" if set_name == "powsledm" else "1"
    elif automatic_network and set_name != "vonr":
        mandatory_relay = spec.nvram_scheme in {"car", "link_role"} and (
            index == (4 if spec.nvram_game == "srallyc" else
                      8 if spec.nvram_game in {"stcc", "stcca", "stccb", "stcco"}
                      else 2)
        )
        is_relay = mandatory_relay or (include_relay and index == cabinets - 1)
        options[f"sm2_automatic_network_{set_name}"] = (
            "r" if is_relay else str(index + 1)
        )
    elif automatic_network:
        options["sm2_nvram_von_network_link_attribute"] = "no_link"
    elif spec.nvram_scheme == "daytona":
        options[f"sm2_nvram_{spec.nvram_game}_link_id"] = (
            "master" if index == 0 else "slave"
        )
        options[f"sm2_nvram_{spec.nvram_game}_car_number"] = str(index + 1)
    elif spec.nvram_scheme == "car":
        car_limit = 4 if spec.nvram_game == "srallyc" else 8
        is_relay = index == cabinets - 1 if include_relay else index == car_limit
        options[f"sm2_nvram_{spec.nvram_game}_link_type"] = (
            "relay" if is_relay else f"car_{index + 1}"
        )
        if spec.nvram_game == "srallyc":
            options["sm2_nvram_srallyc_cabinet_type"] = "twin"
    elif spec.nvram_scheme == "role_id":
        is_live = (
            include_relay
            and spec.nvram_game in {"motoraid", "motoraiddx"}
            and index == cabinets - 1
        )
        network_type = "master" if index == 0 else "slave"
        if is_live:
            network_type = "live"
        options[f"sm2_nvram_{spec.nvram_game}_network_type"] = network_type
        options[f"sm2_nvram_{spec.nvram_game}_cabinet_id"] = str(index + 1)
    elif spec.nvram_scheme == "sgt24h":
        role = "master" if index == 0 else "slave"
        options["sm2_nvram_sgt24h_link_type"] = f"car_no{index + 1}_{role}"
        options["sm2_nvram_sgt24h_link_max"] = str(cabinets)
    elif spec.nvram_scheme == "overrev":
        role = "master" if index == 0 else "slave"
        options["sm2_nvram_overrev_link_max"] = f"{cabinets}_links"
        options["sm2_nvram_overrev_link_type"] = f"{role}_carno_{index + 1}"
    elif spec.nvram_scheme == "link_role":
        options[f"sm2_nvram_{spec.nvram_game}_link_type"] = (
            "master" if index == 0 else "slave" if index == 1 else "relay"
        )
    elif spec.nvram_scheme == "network_attribute":
        options["sm2_nvram_von_network_link_attribute"] = (
            "master" if index == 0 else "slave"
        )
    elif spec.nvram_scheme == "relay_program":
        options["sm2_nvram_von_network_link_attribute"] = "no_link"
    else:
        raise RuntimeError(f"unsupported NVRAM scheme: {spec.nvram_scheme}")
    path = root / "config" / "core-options.cfg"
    path.write_text(
        "".join(f"{key} = {json.dumps(value)}\n" for key, value in options.items()),
        encoding="utf-8",
    )


def terminate_instance(process: subprocess.Popen[bytes]) -> bool:
    if process.poll() is not None:
        return False
    process.terminate()
    try:
        process.wait(timeout=5.0)
        return False
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5.0)
        return True


def log_contains(path: Path, text: str) -> bool:
    try:
        return text in path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return False


def close_instance(process: subprocess.Popen[bytes], command_port: int) -> bool:
    if process.poll() is not None:
        return False
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(b"QUIT\n", ("127.0.0.1", command_port))
        process.wait(timeout=8.0)
        return False
    except (OSError, subprocess.TimeoutExpired):
        if sys.platform != "darwin":
            return terminate_instance(process)
        try:
            post_escape_to_pid(process.pid)
            time.sleep(1.0)
            if process.poll() is None:
                post_escape_to_pid(process.pid)
            process.wait(timeout=5.0)
            return False
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            return terminate_instance(process)


def recover_unsaved_core_options(root: Path, log: Path) -> dict[str, str]:
    """Retain queried values lost by a clean native-window quit, per instance.

    A frontend save after the observation is authoritative. Never invent a
    value for unqueried options or import keys absent from its options file.
    """
    path = root / "config/core-options.cfg"
    if not path.exists() or not log.exists():
        return {}
    text = log.read_text(encoding="utf-8", errors="replace")
    saved_marker = f'Saved core options file to "{path}"'
    saved_at = text.rfind(saved_marker)
    current_text = path.read_text()
    current = dict(re.findall(r'^([^\s=]+) = "([^"\n]*)"$', current_text, re.M))
    observed = {}
    for match in re.finditer(r'\[Environ\] GET_VARIABLE: (sm2_[A-Za-z0-9_]+) = "([^"\n]*)"', text):
        if match.start() > saved_at and match[1] in current:
            observed[match[1]] = match[2]
    changed = {key: value for key, value in observed.items() if current[key] != value}
    if changed:
        backup = path.with_name("core-options-before-exit-recovery.cfg")
        shutil.copy2(path, backup)
        updated = re.sub(r'^([^\s=]+) = "([^"\n]*)"$',
                         lambda match: f'{match[1]} = {json.dumps(changed[match[1]])}'
                         if match[1] in changed else match[0], current_text, flags=re.M)
        path.write_text(updated)
    return changed


def resolve_content(path: Path, assets: Path, staging: Path | None = None) -> Path:
    """Give RetroArch an empty content entry for an absent declared donor set.

    ROMs remain in the user's directory; the owned run contains sibling links
    and a 22-byte empty ZIP identifying the reconstructed set, never ROM copies.
    """
    path = path.expanduser().resolve()
    if path.exists():
        return path
    game = next((g for g in ET.parse(assets / "games.xml").getroot().findall("game")
                 if g.get("name") == path.stem), None)
    if game is None or not game.get("rom_fallback"):
        raise FileNotFoundError(path)
    if staging is None:
        return path
    staging.mkdir(parents=True, exist_ok=True)
    for sibling in path.parent.iterdir():
        if sibling.suffix.lower() in {".zip", ".7z"}:
            target = staging / sibling.name
            if not target.exists():
                target.symlink_to(sibling)
    entry = staging / path.name
    with zipfile.ZipFile(entry, "w"):
        pass
    return entry


def validate_paths(
    args: argparse.Namespace, instance_indices: list[int],
) -> tuple[Path, Path, Path, Path, Path, Path | None, Path | None]:
    retroarch = args.retroarch.expanduser().resolve(strict=True)
    core = args.core.expanduser().resolve(strict=True)
    assets = args.system_assets.expanduser().resolve(strict=True)
    rom = resolve_content(args.rom, assets)
    base_config = args.base_config.expanduser().resolve(strict=True)
    relay_rom = args.relay_rom.expanduser().resolve(strict=True) if args.relay_rom else None
    input_replay = (
        args.input_replay.expanduser().resolve(strict=True)
        if args.input_replay else None
    )
    if not assets.is_dir() or not (assets / "games.xml").is_file():
        raise RuntimeError(f"invalid SM2 system-assets directory: {assets}")
    if rom.stem != args.set_name:
        raise RuntimeError(f"ROM filename {rom.name!r} does not match --set-name {args.set_name!r}")
    if args.instance_games:
        games = args.instance_games.split(",")
        if len(games) != args.cabinets or games[0] != args.set_name:
            raise RuntimeError("--instance-games must match the total and start with --set-name")
        for game in games:
            if not re.fullmatch(r"[A-Za-z0-9_-]+", game):
                raise RuntimeError("invalid ROM name in --instance-games")
            resolve_content(rom.parent / f"{game}.zip", assets)
        return retroarch, core, rom, base_config, assets, relay_rom, input_replay
    needs_local_von_relay = (
        args.set_name in VIRTUAL_ON_TWIN_SETS
        and args.cabinets == 3
        and 2 in instance_indices
    )
    if args.set_name == "powsledm":
        if args.cabinets != 3:
            raise RuntimeError("Power Sled requires three native programs")
        if relay_rom is None or relay_rom.stem != "powsledr":
            raise RuntimeError("Power Sled requires --relay-rom powsledr.zip")
        if args.slave_rom is None or args.slave_rom.stem != "powsled":
            raise RuntimeError("Power Sled requires --slave-rom powsled.zip")
        args.slave_rom = args.slave_rom.expanduser().resolve(strict=True)
    elif args.slave_rom is not None or args.set_name in {"powsled", "powsledr"}:
        raise RuntimeError("Start Power Sled with --set-name powsledm and both peer ROMs")
    elif needs_local_von_relay:
        if relay_rom is None or relay_rom.stem != "vonr":
            raise RuntimeError("three-instance Virtual On requires --relay-rom vonr.zip")
    elif relay_rom is not None:
        raise RuntimeError("--relay-rom is used only by three-instance Virtual On")
    return retroarch, core, rom, base_config, assets, relay_rom, input_replay


def baseline_directory(baseline: Path, role: str, game: str, index: int) -> Path:
    """Resume the same program after the launcher's participant/folder reorder."""
    manifest_path = baseline / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        pairs = list(zip(manifest["roles"], manifest["instance_sets"]))
        if (role, game) in pairs:
            return baseline / role
        matching = [old_role for old_role, old_game in pairs if old_game == game]
        if len(matching) == 1:
            return baseline / matching[0]
        if index < len(pairs) and pairs[index][1] == game:
            return baseline / pairs[index][0]
    return baseline / role


def main() -> int:
    args = parse_args()
    spec = game_spec(args.set_name)
    if args.interactive and (args.input_replay or args.input_replay_map or args.operator_recipe
                             or args.service_menu or args.network_exercise):
        raise RuntimeError("interactive play cannot be combined with scripted input or exercises")
    if args.window_layout == "power-sled" and args.set_name != "powsledm":
        raise RuntimeError("Power Sled layout requires --set-name powsledm")
    operator_actions = None
    operator_targets = []
    operator_label = action_label
    recipe = None
    if args.operator_recipe:
        if args.network_exercise:
            raise RuntimeError("Network exercises cannot run inside an operator campaign")
        if args.set_name != "powsledm" or args.service_menu or args.automatic_network or args.cabinets != 3 or args.instance_indices:
            raise RuntimeError("--operator-recipe requires all three Power Sled programs and no --service-menu/--automatic-network")
        recipe = args.operator_recipe.expanduser().resolve(strict=True)
        with recipe.open("rb") as stream:
            campaign = tomllib.load(stream)
        if not args.sample:
            from power_sled_campaign import run_campaign
            return run_campaign(args, campaign, recipe)
        selected = [s for s in campaign.get("samples", []) if s.get("suffix") == args.sample]
        if len(selected) != 1:
            raise RuntimeError("operator sample suffix must identify exactly one recipe")
        from power_sled_campaign import compile_sample, action_label as power_action_label
        operator_label = power_action_label
        operator_actions, operator_targets = compile_sample(selected[0], campaign.get("macros", {}))
        if any(a.kind not in {"button", "wait", "screenshot", "close", "ride_cycle"} for a in operator_actions):
            raise RuntimeError("linked operator recipes support buttons, waits, screenshots and final CLOSE")
    elif args.sample:
        raise RuntimeError("--sample requires --operator-recipe")
    if not args.instance_games and args.cabinets > spec.max_cabinets:
        raise RuntimeError(
            f"{args.set_name} supports at most {spec.max_cabinets} linked cabinets"
        )
    if not 1 <= args.menu_frame_samples <= 20 or (args.menu_frame_samples > 1 and not args.service_menu):
        raise RuntimeError("--menu-frame-samples requires --service-menu and a value from 1 to 20")
    if not 1 <= args.screenshot_samples <= 20 or (args.screenshot_samples > 1 and not args.capture_screenshots):
        raise RuntimeError("--screenshot-samples requires --capture-screenshots and a value from 1 to 20")
    if not 0 <= args.screenshot_gap <= 60:
        raise RuntimeError("--screenshot-gap must be from 0 to 60 seconds")
    if args.service_menu and args.set_name != "powsledm":
        raise RuntimeError("--service-menu is restricted to the Power Sled communication check")
    if args.window_columns < 1:
        raise RuntimeError("--window-columns must be at least 1")
    if args.include_relay and not args.instance_games:
        if args.set_name not in OPTIONAL_RELAY_SETS:
            raise RuntimeError(
                f"{args.set_name} does not use the optional Relay/Live role"
            )
        if args.cabinets < 3:
            raise RuntimeError("--include-relay requires at least three cabinets")
    instance_indices = local_instance_indices(args.instance_indices, args.cabinets)
    (
        retroarch, core, rom, base_config, assets, relay_rom, input_replay,
    ) = validate_paths(args, instance_indices)
    running = retroarch_processes(retroarch)
    if running and not args.allow_existing_retroarch:
        details = ", ".join(str(pid) for pid, _ in running)
        raise RuntimeError(f"RetroArch is already running (PID {details}); no test was started")
    replay_map = {}
    if args.input_replay_map:
        replay_map = json.loads(args.input_replay_map.read_text())
        if not isinstance(replay_map, dict) or any(
                not isinstance(role, str) or not isinstance(path, str)
                for role, path in replay_map.items()):
            raise RuntimeError("--input-replay-map requires role-to-path strings")
        replay_map = {role: Path(path).expanduser().resolve(strict=True)
                      for role, path in replay_map.items()}
    if args.cabinets > 1 and 0 in instance_indices and not port_available(args.port):
        raise RuntimeError(f"netplay port {args.port} is already in use")

    if args.output:
        output = args.output.expanduser().resolve()
        output.mkdir(parents=True, exist_ok=False)
    else:
        output = Path(tempfile.mkdtemp(prefix=f"sm2-netpacket-{args.set_name}-"))

    rom = resolve_content(rom, assets, output / "content")

    roles = ["host" if index == 0 else f"client{index}" for index in instance_indices]
    if args.instance_roles:
        names = args.instance_roles.split(",")
        if (len(names) != args.cabinets or names[0] != "host"
                or len(set(names)) != len(names)
                or any(not re.fullmatch(r"[A-Za-z0-9_-]+", name) for name in names)):
            raise RuntimeError("--instance-roles requires unique folder names with host first")
        roles = [names[index] for index in instance_indices]
    controller_indices = None
    if args.controller_indices is not None:
        controller_indices = [None if value == "none" else int(value)
                              for value in args.controller_indices.split(",")]
        assigned_indices = [value for value in controller_indices if value is not None]
        if (len(controller_indices) != len(roles) or any(value < 0 or value >= 16 for value in assigned_indices)
                or len(set(assigned_indices)) != len(assigned_indices)):
            raise RuntimeError("--controller-indices requires one distinct index 0..15 or none per local instance")
    controller_names = (mac_controller_names(controller_indices)
                        if controller_indices is not None and sys.platform == "darwin" else None)
    if controller_names:
        for role, index, name in zip(roles, controller_indices, controller_names):
            label = "No Gamepad" if index is None else f"Gamepad {index + 1}: {name}"
            print(f"{label} -> {role}", flush=True)
    instance_sets = [args.set_name for _ in roles]
    instance_roms = [rom for _ in roles]
    if args.instance_games:
        games = args.instance_games.split(",")
        instance_sets = [games[index] for index in instance_indices]
        instance_roms = [resolve_content(rom.parent / f"{game}.zip", assets, output / "content")
                         for game in instance_sets]
    elif args.set_name == "powsledm":
        for position, index in enumerate(instance_indices):
            instance_sets[position] = ("powsledm", "powsledr", "powsled")[index]
            instance_roms[position] = (rom, relay_rom, args.slave_rom)[index]
    elif relay_rom is not None and 2 in instance_indices:
        relay_position = instance_indices.index(2)
        instance_sets[relay_position] = "vonr"
        instance_roms[relay_position] = relay_rom
    power_ring = args.set_name == "powsledm" and all(
        game in {"powsledm", "powsledr", "powsled"} for game in instance_sets)
    command_ports = [free_udp_port() for _ in roles]
    if len(set(command_ports)) != len(command_ports) or args.port in command_ports:
        raise RuntimeError("could not allocate distinct RetroArch command ports")
    remote_ports = [free_udp_port() for _ in roles] if args.service_menu or operator_actions else []
    if len(set(command_ports + remote_ports + [args.port])) != len(command_ports + remote_ports) + 1:
        raise RuntimeError("could not allocate distinct network command/input ports")
    configs: list[Path] = []
    input_replays: list[Path | None] = []
    desktop = None
    if args.fit_windows or args.desktop_size:
        if args.window_layout == "cascade":
            raise RuntimeError("desktop fitting requires a grid layout")
        desktop = usable_desktop(args.desktop_size)
        global WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_FRAME_WIDTH, WINDOW_FRAME_HEIGHT, WINDOW_ORIGIN_X, WINDOW_ORIGIN_Y
        columns = 2 if args.window_layout == "power-sled" else args.window_columns
        WINDOW_WIDTH, WINDOW_HEIGHT = fitted_window_size(args.cabinets, columns, desktop[2], desktop[3])
        WINDOW_FRAME_WIDTH, WINDOW_FRAME_HEIGHT = WINDOW_WIDTH + 16, WINDOW_HEIGHT + 28
        WINDOW_ORIGIN_X, WINDOW_ORIGIN_Y = desktop[0] + 24, desktop[1] + 24
        print(f"Usable desktop: {desktop[2]}x{desktop[3]}; each window: {WINDOW_WIDTH}x{WINDOW_HEIGHT}", flush=True)
    window_positions = [
        window_position(("powsledm", "powsledr", "powsled").index(game)
                        if args.window_layout == "power-sled" else index,
                        args.window_layout, args.window_columns)
        for index, game in zip(instance_indices, instance_sets)
    ]
    for local_index, (index, role) in enumerate(zip(instance_indices, roles)):
        root = output / role
        window_x, window_y = window_positions[local_index]
        configs.append(write_config(root, assets, base_config, args.port,
                                    command_ports[local_index], args.cabinets,
                                    window_x, window_y,
                                    remote_ports[local_index] if remote_ports else None))
        if controller_indices is not None:
            config = root / "netpacket-overrides.cfg"
            write_controller_config(config, controller_indices[local_index],
                                    controller_names[local_index] if controller_names else None)
        replay_source = replay_map.get(role, input_replay)
        local_replay = root / "input.replay" if replay_source else None
        if replay_source and local_replay:
            shutil.copy2(replay_source, local_replay)
        input_replays.append(local_replay)
        if args.baseline_run:
            baseline = baseline_directory(args.baseline_run.expanduser().resolve(strict=True),
                                          role, instance_sets[local_index], index)
            sources = find_saves(baseline, instance_sets[local_index])
            if len(sources) != 1 and not (args.instance_games and not sources):
                raise RuntimeError(f"missing unique target-core baseline for {instance_sets[local_index]}")
            if sources:
                shutil.copy2(sources[0], root / "saves" / sources[0].name)
        write_options(
            root, instance_sets[local_index], args.cabinets, index,
            args.include_relay, args.automatic_network,
        )
        if args.record_audio or args.play_audio:
            config = root / "netpacket-overrides.cfg"
            driver = "coreaudio" if sys.platform == "darwin" else "alsa"
            settings = config.read_text().replace('audio_enable = "false"', 'audio_enable = "true"')
            settings = settings.replace('audio_driver = "null"', f'audio_driver = "{driver}"')
            config.write_text(settings + 'audio_sync = "false"\nrecord_driver = "wav"\n')
        if args.native_nvram_baseline:
            source = args.native_nvram_baseline.expanduser().resolve(strict=True) / role
            for extension in ("nv", "eeprom"):
                name = instance_sets[local_index] + "." + extension
                shutil.copy2(source / name, root / "saves" / name)
        if args.core_options_override:
            overrides = json.loads(args.core_options_override.read_text())
            selected_options = overrides.get(role, overrides.get(instance_sets[local_index], {}))
            if not isinstance(selected_options, dict) or any(
                    not isinstance(key, str) or not key.startswith("sm2_")
                    or not isinstance(value, str) for key, value in selected_options.items()):
                raise RuntimeError("Core Option overrides must map sm2_ keys to string values")
            option_path = root / "config" / "core-options.cfg"
            current = dict(re.findall(r'^([^\s=]+) = "([^"\n]*)"$', option_path.read_text(), re.M))
            current.update(selected_options)
            option_path.write_text("".join(f"{key} = {json.dumps(value)}\n" for key, value in current.items()))

    manifest = {
        "result_scope": "process-lifecycle" if args.instance_games or args.cabinets == 1 else "linked-network",
        "retroarch": str(retroarch),
        "core": str(core),
        "core_sha256": hashlib.sha256(core.read_bytes()).hexdigest(),
        "operator_recipe": str(recipe) if recipe else None,
        "operator_recipe_sha256": hashlib.sha256(recipe.read_bytes()).hexdigest() if recipe else None,
        "operator_sample": args.sample,
        "operator_actions": [operator_label(a) for a in operator_actions] if operator_actions else [],
        "operator_targets": operator_targets,
        "baseline_run": str(args.baseline_run.resolve()) if args.baseline_run else None,
        "core_options_override": str(args.core_options_override.resolve()) if args.core_options_override else None,
        "native_nvram_baseline": str(args.native_nvram_baseline.resolve()) if args.native_nvram_baseline else None,
        "rom": str(rom),
        "base_config": str(base_config),
        "set_name": args.set_name,
        "instance_sets": instance_sets,
        "instance_roms": [str(path) for path in instance_roms],
        "cabinets": args.cabinets,
        "existing_retroarch_pids": [pid for pid, _ in running],
        "instance_indices": instance_indices,
        "connect_host": args.connect_host,
        "include_relay": args.include_relay,
        "automatic_network": args.automatic_network,
        "interactive": args.interactive,
        "controller_indices": controller_indices,
        "controller_devices": controller_names,
        "port": args.port,
        "command_ports": command_ports,
        "roles": roles,
        "window_layout": args.window_layout,
        "window_columns": args.window_columns,
        "usable_desktop": desktop,
        "capture_screenshots": args.capture_screenshots,
        "screenshot_samples": args.screenshot_samples,
        "screenshot_gap": args.screenshot_gap,
        "input_replay": str(input_replay) if input_replay else None,
        "input_replay_map": {role: {"path": str(path),
                                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                             for role, path in replay_map.items()},
        "record_audio": args.record_audio,
        "service_menu_requested": args.service_menu,
        "menu_frame_samples": args.menu_frame_samples,
        "remote_input_ports": remote_ports,
        "window_positions": [
            {"role": role, "x": position[0], "y": position[1],
             "content_width": WINDOW_WIDTH, "content_height": WINDOW_HEIGHT,
             "frame_width": WINDOW_FRAME_WIDTH,
             "frame_height": WINDOW_FRAME_HEIGHT}
            for role, position in zip(roles, window_positions)
        ],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if args.dry_run:
        print(json.dumps({**manifest, "output": str(output), "status": "dry-run"}, indent=2))
        return 0

    processes: list[subprocess.Popen[bytes]] = []
    logs: list[object] = []
    results: list[InstanceResult] = []
    success = False
    completed_run = False
    exercise_result = None
    instance_commands = []
    previous_ignore_state = read_ignore_state()
    atexit.register(write_ignore_state, previous_ignore_state)
    write_ignore_state(True)
    try:
        for local_index, (index, role) in enumerate(zip(instance_indices, roles)):
            log_path = output / f"{role}.log"
            log = log_path.open("wb")
            logs.append(log)
            netplay = ([] if args.cabinets == 1 else
                       ["-H"] if index == 0 else ["-C", args.connect_host])
            replay = ["-P", str(input_replays[local_index])] if input_replays[local_index] else []
            recording = ["-r", str(output / role / "audio.wav")] if args.record_audio else []
            command = [
                str(retroarch), "-v", *configs[local_index],
                "-L", str(core), *replay, *recording, *netplay, str(instance_roms[local_index]),
            ]
            instance_commands.append(command)
            environment = os.environ.copy()
            if controller_indices is not None:
                environment["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
            process = subprocess.Popen(command, cwd=output, stdout=log,
                                       stderr=subprocess.STDOUT, env=environment)
            processes.append(process)
            results.append(InstanceResult(role, process.pid, log=str(log_path)))
            (output / "pids.json").write_text(
                json.dumps([asdict(item) for item in results], indent=2) + "\n"
            )
            if sys.platform == "darwin":
                activate_process(process)
                # ROM loading can leave the process visible before its window
                # exists. Keep the wait bounded without changing other windows.
                position_process_window(process, *window_positions[local_index], timeout=30.0)
            wait_while_alive(process, args.startup_wait)

        # Core initialization can overwrite the configured size. Apply outer
        # frames after every instance has finished its startup wait, and retain
        # read-back evidence instead of treating config values as actual sizes.
        if desktop is not None and sys.platform == "darwin":
            manifest["actual_window_frames"] = [
                {"role": item.role, **fit_process_window(process, *position,
                    WINDOW_FRAME_WIDTH, WINDOW_FRAME_HEIGHT)}
                for item, process, position in zip(results, processes, window_positions)
            ]
            (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

        deadline = time.monotonic() + args.settle
        while time.monotonic() < deadline:
            exited = [(item.role, process.returncode) for item, process in zip(results, processes)
                      if process.poll() is not None]
            if exited:
                raise RuntimeError(f"RetroArch exited during the linked-cabinet run: {exited}")
            time.sleep(0.20)
        if operator_actions:
            for action, targets in zip(operator_actions, operator_targets):
                if any(process.poll() is not None for process in processes):
                    raise RuntimeError("RetroArch exited during operator sequence")
                if action.kind == "button":
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        selected_ports = [p for p, game in zip(remote_ports, instance_sets) if game in targets]
                        for remote_port in selected_ports:
                            send_button_state(sock, remote_port, str(action.value), True)
                        time.sleep(0.6)
                        for remote_port in selected_ports:
                            send_button_state(sock, remote_port, str(action.value), False)
                    time.sleep(0.6)
                elif action.kind == "ride_cycle":
                    from power_sled_campaign import Screens
                    screens = Screens()
                    local_index = instance_sets.index(targets[0])
                    process, item = processes[local_index], results[local_index]
                    root = output/item.role
                    picture = take_screenshot(process,root,command_ports[local_index],'ride-cycle-start')
                    target = int(action.value)
                    if screens.ride(picture,targets[0])!=target:
                        raise RuntimeError('Ride cycle initial color differs from recipe')
                    previous = target
                    for cycle_index in range(1,4):
                        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
                            send_button_state(sock,remote_ports[local_index],'A',True)
                            time.sleep(0.6)
                            send_button_state(sock,remote_ports[local_index],'A',False)
                        time.sleep(0.6)
                        picture = take_screenshot(process,root,command_ports[local_index],f'ride-cycle-{cycle_index:02d}')
                        value = screens.ride(picture,targets[0])
                        if value==previous: raise RuntimeError('Ride selection did not advance')
                        previous = value
                        if value==target: break
                    else: raise RuntimeError('Ride cycle did not close within three native calls')
                elif action.kind == "wait":
                    time.sleep(float(action.value))
                elif action.kind == "screenshot":
                    for local_index, (item, process) in enumerate(zip(results, processes)):
                        if instance_sets[local_index] in targets:
                            take_screenshot(process, output / item.role, command_ports[local_index], str(action.value))
                # Final CLOSE is performed for all peers by the existing lifecycle.
        if args.service_menu:
            def press_all(button: str) -> None:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    for remote_port in remote_ports:
                        send_button_state(sock, remote_port, button, True)
                    time.sleep(0.6)
                    for remote_port in remote_ports:
                        send_button_state(sock, remote_port, button, False)
                time.sleep(0.6)
            press_all("R3")
            for local_index, (item, process) in enumerate(zip(results, processes)):
                take_screenshot(process, output / item.role,
                                command_ports[local_index], "service-root")
            for sample_index in range(1, args.menu_frame_samples):
                for local_index, (item, process) in enumerate(zip(results, processes)):
                    take_screenshot(process, output / item.role, command_ports[local_index],
                                    f"service-root-{sample_index:02d}")
                time.sleep(0.17)
            for _ in range(6):
                press_all("L3")
            press_all("A")
            time.sleep(2)
        if args.capture_screenshots:
            for sample_index in range(args.screenshot_samples):
                if sample_index:
                    for process in processes:
                        if process.poll() is not None:
                            raise RuntimeError("RetroArch exited during screenshot observations")
                    time.sleep(args.screenshot_gap)
                for local_index, (item, process) in enumerate(zip(results, processes)):
                    root = output / item.role
                    label = (item.role if args.screenshot_samples == 1
                             else f"{item.role}-{sample_index+1:02d}")
                    item.screenshot = str(take_screenshot(
                        process, root, command_ports[local_index], label
                    ))
        if args.service_menu:
            for sample_index in range(1, args.menu_frame_samples):
                for local_index, (item, process) in enumerate(zip(results, processes)):
                    take_screenshot(process, output / item.role, command_ports[local_index],
                                    f"assignments-{sample_index:02d}")
                time.sleep(0.17)
        if args.network_exercise:
            from retroarch_network_exercise import exercise
            exercise_result=exercise(args.network_exercise,processes,results,
                [output/role for role in roles],command_ports,instance_commands,logs,
                output,close_instance)
        # Interactive users can already open menus, minimize or close windows.
        # Do not turn their UI interaction into a startup/lifecycle failure.
        if desktop is not None and sys.platform == "darwin" and not args.interactive:
            observed = []
            for item, process, position in zip(results, processes, window_positions):
                frame = fit_process_window(process, *position,
                    WINDOW_FRAME_WIDTH, WINDOW_FRAME_HEIGHT, apply=False)
                if frame is not None:
                    observed.append({"role": item.role, **frame})
            manifest["final_window_frames"] = observed
            (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        if args.interactive:
            print(f"Cabinets running. Session: {output}\nClose a cabinet or press Ctrl+C to stop the group.", flush=True)
            try:
                while all(process.poll() is None for process in processes):
                    time.sleep(0.2)
            except KeyboardInterrupt:
                pass
        completed_run = True
    finally:
        for index in reversed(range(len(processes))):
            item = results[index]
            process = processes[index]
            item.forced_kill = close_instance(process, command_ports[index])
            item.exit_code = process.returncode
        for log in logs:
            log.close()

        if args.interactive:
            manifest["recovered_core_options"] = {
                item.role: recover_unsaved_core_options(output / item.role, Path(item.log))
                for item in results if item.exit_code == 0 and not item.forced_kill
            }
            (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

        roster_marker = f", {args.cabinets} cabinets"
        for item in results:
            item.roster_ready = (
                log_contains(Path(item.log), "Linked-cabinet roster ready: participant ")
                and log_contains(Path(item.log), roster_marker)
            )
        if power_ring:
            for local_index, item in enumerate(results):
                index = instance_indices[local_index]
                native_id = 1 if index == 0 else args.cabinets - index + 1
                item.native_link_ready = log_contains(Path(item.log),
                    f"Native board {instance_sets[local_index]}: enabled=1 alive=1 "
                    f"id={native_id} count={args.cabinets}")
        if args.instance_games or args.cabinets == 1:
            # Interactive launcher success describes process lifecycle only.
            # The core owns compatibility and reports any connection problem.
            success = (completed_run and len(results) == len(instance_indices)
                       and all(item.exit_code == 0 and not item.forced_kill for item in results))
        else:
            host_result = next((item for item in results if item.role == "host"), None)
            host_log = Path(host_result.log) if host_result else None
            host_complete = host_log is None or all(
                log_contains(host_log, f"Slave cabinet connected ({count}/{args.cabinets})")
                for count in range(2, args.cabinets + 1)
            )
            logs_clean = all(
                not log_contains(Path(item.log), marker)
                for item in results
                for marker in (
                    "Additional cabinet rejected",
                    "Linked cabinets use different games",
                    "Failed to connect to host",
                )
            )
            success = (completed_run and len(results) == len(instance_indices)
                       and all(item.roster_ready for item in results)
                       and host_complete and logs_clean
                       and (args.set_name != "powsledm"
                            or all(item.native_link_ready for item in results)))

        operator_saves = []
        if operator_actions and success:
            for local_index, item in enumerate(results):
                game = instance_sets[local_index]
                paths = find_saves(output / item.role, game)
                if len(paths) != 1 or item.exit_code != 0 or item.forced_kill:
                    success = False
                    continue
                path = paths[0]
                image = path.read_bytes()
                if (len(image) != 64 + 16384 + 128 or image[:8] != b"SM2SRAM\0"
                    or image[24:56].split(b"\0")[0].decode() != game
                    or int.from_bytes(image[20:24], "little") != binascii.crc_hqx(image[64:], 0)):
                    success = False
                    continue
                native = output / item.role / "samples"
                native.mkdir(exist_ok=True)
                (native / f"{game}.nv").write_bytes(image[64:64+16384])
                (native / f"{game}.eeprom").write_bytes(image[64+16384:])
                operator_saves.append({"set": game, "srm": str(path),
                    "sha256": hashlib.sha256(image).hexdigest(),
                    "backup_ram": str(native / f"{game}.nv"),
                    "eeprom": str(native / f"{game}.eeprom"),
                    "status": "Captured; Native Persistence Requires Separate Reload Review"})

        residual = [(pid, command) for pid, command in retroarch_processes(retroarch)
                    if pid in {item.pid for item in results}]
        report = {
            **manifest,
            "output": str(output),
            "status": "ok" if success and not residual else "failed",
            "instances": [asdict(item) for item in results],
            "operator_saves": operator_saves,
            "residual_processes": [pid for pid, _ in residual],
            "network_exercise": exercise_result,
        }
        (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        write_ignore_state(previous_ignore_state)
        atexit.unregister(write_ignore_state)
        if residual:
            raise RuntimeError(f"launched RetroArch processes still alive: {residual}")
    return 0 if success else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print(f"error: {error}", file=os.sys.stderr)
        raise SystemExit(1)
