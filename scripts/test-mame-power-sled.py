#!/usr/bin/env python3
"""Bounded, isolated Power Sled MAME ring reference; no ROM/config mutation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time

LUA = r'''
local machine = manager.machine
local space = machine.devices[":maincpu"].spaces["program"]
local out = assert(io.open(OUTPUT .. "/probe.jsonl", "w"))
local next_log = 0
local shots = {2, 8, 15, 24, 32, 40, 45, 48, 51, 56, 58}
local shot_index = 1
local actions = {}
if MODE == "service" then
  actions = {{25, ":IN0", 0x04}, {34, ":IN0", 0x40}, {43, ":IN1", 0x01}, {50, ":IN1", 0x02}}
end
if MODE == "assignments" then
  actions = {{25, ":IN0", 0x04}, {29, ":IN0", 0x40}, {31, ":IN0", 0x40},
    {33, ":IN0", 0x40}, {35, ":IN0", 0x40}, {37, ":IN0", 0x40}, {39, ":IN0", 0x40},
    {43, ":IN1", 0x02}, {49, ":IN0", 0x04}, {55, ":IN0", 0x10}}
end
if MODE == "ride-id" then
  actions = {{25, ":IN0", 0x04}, {29, ":IN0", 0x40}, {31, ":IN0", 0x40},
    {33, ":IN0", 0x40}, {35, ":IN0", 0x40}, {37, ":IN0", 0x40}, {39, ":IN0", 0x40},
    {41, ":IN1", 0x02}, {45, ":IN0", 0x40}, {47, ":IN0", 0x40}, {49, ":IN1", 0x02}}
end
if MODE == "ride-id-cycle" then
  actions = {{25, ":IN0", 0x04}, {29, ":IN0", 0x40}, {31, ":IN0", 0x40},
    {33, ":IN0", 0x40}, {35, ":IN0", 0x40}, {37, ":IN0", 0x40}, {39, ":IN0", 0x40},
    {41, ":IN1", 0x02}, {45, ":IN0", 0x40}, {47, ":IN0", 0x40}, {49, ":IN1", 0x02},
    {53, ":IN0", 0x40}, {55, ":IN0", 0x40}}
  shots = {24, 51, 56}
  for t = 57, 89, 2 do
    actions[#actions+1] = {t, ":IN1", 0x02}
    shots[#shots+1] = t+1
  end
end
if PLAN then actions = PLAN.actions; shots = PLAN.shots end
local hold = PLAN and PLAN.input_hold or 0.6
local states = {}
local function sample(t)
  local bytes = {}
  for i = 0, 0x1f do bytes[#bytes+1] = string.format("%02x", space:read_u8(0x01a00000+i)) end
  out:write(string.format('{"seconds":%.3f,"shared_00_1f":"%s"}\n', t, table.concat(bytes)))
  out:flush()
end
emu.register_frame_done(function ()
  local t = machine.time:as_double()
  if t >= next_log then sample(t); next_log = math.floor(t)+1 end
  for i, action in ipairs(actions) do
    local active = t >= action[1] and t < action[1]+hold
    if active or states[i] == true then
      local field = machine.ioport.ports[action[2]]:field(action[3])
      if active then field:set_value(1) else field:clear_value() end
      if active and not states[i] then print(string.format("POWSLED_PROBE input %s mask %02x at %.3f",action[2],action[3],t)) end
      states[i] = active
    end
  end
  if shot_index <= #shots and t >= shots[shot_index] then
    for tag, screen in pairs(machine.screens) do
      local filename = PLAN and PLAN.precise_shots
        and string.format("/screen-%04d.png", shot_index)
        or string.format("/screen-%02d.png", shots[shot_index])
      local err = screen:snapshot(OUTPUT .. filename)
      if PLAN and PLAN.backup_snapshots then
        local bytes = {}
        for offset = 0, 0x3fff do
          bytes[#bytes+1] = string.char(space:read_u8(0x01d00000+offset))
        end
        local backup = assert(io.open(OUTPUT .. string.format("/backup-%04d.bin", shot_index), "wb"))
        backup:write(table.concat(bytes)); backup:close()
      end
      print("POWSLED_PROBE snapshot " .. shots[shot_index] .. " " .. tostring(err))
      break
    end
    shot_index = shot_index+1
  end
end)
print("POWSLED_PROBE started " .. machine.system.name)
'''


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mame', type=Path, required=True)
    p.add_argument('--rom-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--sets', nargs='+', default=['powsledm', 'powsledr', 'powsled'])
    p.add_argument('--seconds', type=int, default=60)
    p.add_argument('--wall-timeout', type=int, default=180)
    p.add_argument('--mode', choices=['boot', 'service', 'assignments', 'ride-id', 'ride-id-cycle'], default='boot')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--no-drc', action='store_true', help='Use MAME interpreters for the CPU reference')
    p.add_argument('--plan', type=Path, help='JSON per-unit action/screenshot plan')
    p.add_argument('--seed-from', type=Path, help='Prior evidence root; copy only per-unit NVRAM into new directories')
    a = p.parse_args()
    if not 1 <= len(a.sets) <= 5 or any(s not in ('powsled', 'powsledm', 'powsledr') for s in a.sets):
        p.error('Use one to five Power Sled units')
    if not 10 <= a.seconds <= 300 or not 15 <= a.wall_timeout <= 600:
        p.error('Seconds must be 10..300; wall timeout 15..600')
    a.mame = a.mame.expanduser().resolve()
    a.rom_dir = a.rom_dir.expanduser().resolve()
    a.output = a.output.expanduser().resolve()
    if not a.mame.is_file() or not a.rom_dir.is_dir():
        p.error('MAME executable and ROM directory must exist')
    if a.output.exists():
        p.error('Output must be a new directory to preserve prior evidence')
    # Reserve distinct TCP ports while constructing the ring. MAME binds after release.
    sockets = []
    try:
        for _ in a.sets:
            s = socket.socket()
            s.bind(('127.0.0.1', 0))
            sockets.append(s)
        ports = [s.getsockname()[1] for s in sockets]
    finally:
        for s in sockets:
            s.close()
    plan = json.loads(a.plan.read_text()) if a.plan else {}
    if plan and set(plan) != {f'{i+1}-{name}' for i, name in enumerate(a.sets)}:
        p.error('Plan must contain exactly the requested numbered unit names')
    for unit in plan.values():
        if not 0.05 <= unit.get('input_hold', 0.6) <= 0.6:
            p.error('Input hold must be 0.05..0.6 seconds')
        if not isinstance(unit.get('precise_shots', False), bool):
            p.error('precise_shots must be boolean')
        if not isinstance(unit.get('backup_snapshots', False), bool):
            p.error('backup_snapshots must be boolean')
        if not isinstance(unit.get('actions'), list) or not isinstance(unit.get('shots'), list):
            p.error('Each plan unit needs actions and shots lists')
        for action in unit['actions']:
            if len(action) != 3 or not 0 <= action[0] < a.seconds or action[1] not in (':IN0', ':IN1') or action[2] not in (1, 2, 4, 8, 16, 32, 64, 128):
                p.error('Invalid bounded digital-input action')
        if unit['shots'] != sorted(unit['shots']) or any(not 0 <= t < a.seconds for t in unit['shots']):
            p.error('Snapshot times must be sorted and within the run')
    if a.seed_from:
        a.seed_from = a.seed_from.resolve()
        for i, name in enumerate(a.sets):
            if not (a.seed_from/f'{i+1}-{name}'/'nvram'/name).is_dir():
                p.error('Seed must provide per-unit native NVRAM directories')
    records = []
    for i, name in enumerate(a.sets):
        d = a.output / f'{i+1}-{name}'
        cmd = [str(a.mame), name, '-noreadconfig', '-rompath', str(a.rom_dir),
               '-homepath', str(d), '-inipath', str(d), '-cfg_directory', str(d/'cfg'),
               '-nvram_directory', str(d/'nvram'), '-state_directory', str(d/'sta'),
               '-snapshot_directory', str(d), '-diff_directory', str(d/'diff'),
               '-input_directory', str(d/'inp'), '-noplugins', '-skip_gameinfo',
               '-video', 'none', '-sound', 'none', '-throttle', '-sleep',
               '-seconds_to_run', str(a.seconds), '-verbose',
               '-comm_localhost', '127.0.0.1', '-comm_localport', str(ports[i]),
               '-comm_remotehost', '127.0.0.1', '-comm_remoteport', str(ports[(i+1)%len(ports)]),
               '-nocomm_framesync', '-autoboot_script', str(d/'probe.lua')]
        if a.no_drc:
            cmd.append('-nodrc')
        records.append({'set': name, 'directory': str(d), 'command': cmd})
    if a.dry_run:
        print(json.dumps({'dry_run': True, 'units': records}, indent=2))
        return
    a.output.mkdir(parents=True)
    manifest = {'mode': 'custom-plan' if plan else a.mode, 'emulated_seconds': a.seconds, 'wall_timeout': a.wall_timeout,
                'mame_sha256': sha(a.mame), 'mame_version': subprocess.check_output([str(a.mame), '-help'], text=True).splitlines()[0], 'units': records, 'plan': plan, 'seed_from': str(a.seed_from) if a.seed_from else None, 'drc': not a.no_drc,
                'limits': 'Headless source-reference run; no audible output or physical input proof. Frame sync disabled.'}
    processes = []
    handles = []
    start = time.monotonic()
    try:
        for record in records:
            d = Path(record['directory'])
            d.mkdir()
            if a.seed_from:
                import shutil
                shutil.copytree(a.seed_from/d.name/'nvram', d/'nvram')
                record['seed_files'] = {str(f.relative_to(d)): sha(f) for f in (d/'nvram').rglob('*') if f.is_file()}
            def lua(value):
                if isinstance(value, list):
                    return '{'+','.join(lua(v) for v in value)+'}'
                if isinstance(value, dict):
                    return '{'+','.join('['+json.dumps(k)+']='+lua(v) for k,v in value.items())+'}'
                return json.dumps(value)
            custom = 'local PLAN = '+lua(plan[d.name])+'\n' if plan else ''
            (d/'probe.lua').write_text('local OUTPUT = '+json.dumps(str(d))+'\nlocal MODE = '+json.dumps(a.mode)+'\n'+custom+LUA)
            log = (d/'mame.log').open('w')
            handles.append(log)
            proc = subprocess.Popen(record['command'], cwd=d, stdout=log, stderr=subprocess.STDOUT,
                                    start_new_session=True, restore_signals=False)
            record['pid'] = proc.pid
            processes.append(proc)
        while any(proc.poll() is None for proc in processes):
            if time.monotonic()-start >= a.wall_timeout:
                manifest['wall_timeout_reached'] = True
                break
            time.sleep(0.25)
    finally:
        for proc in processes:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
        for proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
        for log in handles:
            log.close()
        for record, proc in zip(records, processes):
            record['returncode'] = proc.returncode
            record['terminated'] = proc.poll() is not None
            d = Path(record['directory'])
            lines = (d/'probe.jsonl').read_text().splitlines() if (d/'probe.jsonl').exists() else []
            record['last_sample_seconds'] = json.loads(lines[-1])['seconds'] if lines else None
            record['screenshots'] = len(list(d.glob('screen-*.png')))
            text = (d/'mame.log').read_text(errors='replace')
            record['probe_ok'] = (bool(lines) and record['last_sample_seconds'] >= a.seconds-2
                                  and record['screenshots'] > 0 and 'LUA ERROR' not in text.upper())
        manifest['wall_seconds'] = round(time.monotonic()-start, 3)
        manifest['files'] = {str(f.relative_to(a.output)): sha(f)
                             for f in sorted(a.output.rglob('*')) if f.is_file()}
        (a.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'output': str(a.output), 'wall_seconds': manifest['wall_seconds'],
                      'units': [{'set': r['set'], 'returncode': r['returncode']} for r in records]}))
    if any(p.returncode != 0 for p in processes) or manifest.get('wall_timeout_reached') or any(not r.get('probe_ok') for r in records):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
