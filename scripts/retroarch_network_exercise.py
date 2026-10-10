"""Bounded runtime network actions for the existing isolated RetroArch runner."""
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import signal
import subprocess
import time
from PIL import Image
from libretro_nvram_samples import take_screenshot

_spec=importlib.util.spec_from_file_location('retroarch_savestate',Path(__file__).with_name('test-retroarch-savestate.py'))
_runner=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_runner)
send_command=_runner.send_command


def exercise(kind, processes, results, roots, ports, commands, logs, output, close_instance):
    phases=[]
    def wait(seconds):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            if any(p.poll() is not None for p in processes):raise RuntimeError('A network test instance exited')
            time.sleep(0.1)
    def capture(label, expected_link=True):
        records=[]
        for process,item,root,port in zip(processes,results,roots,ports):
            text=Path(item.log).read_text(errors='replace')
            states=re.findall(r'Native board \S+: enabled=(\d+) alive=(\d+) id=(\d+) count=(\d+)',text)
            state=list(map(int,states[-1])) if states else None
            picture=take_screenshot(process,root,port,label)
            deadline=time.monotonic()+5
            while True:
                try:
                    with Image.open(picture) as image:image.verify()
                    break
                except (OSError,SyntaxError):
                    if time.monotonic()>=deadline:raise RuntimeError(f'Incomplete screenshot: {picture}')
                    time.sleep(0.05)
            records.append({'role':item.role,'pid':process.pid,'native_state':state,
                            'roster_events':text.count('Linked-cabinet roster ready:'),
                            'overflow': 'Netpacket receive queue overflow' in text,
                            'screenshot':str(picture),'sha256':hashlib.sha256(picture.read_bytes()).hexdigest()})
        ok=all(r['native_state'] and r['native_state'][:2]==[1,1] for r in records)
        phases.append({'phase':label,'expected_link':expected_link,'native_link_ready':ok,'programs':records})
        (output/'network-exercise.json').write_text(json.dumps({'kind':kind,'phases':phases},indent=2)+'\n')
    def reset_all():
        for port in ports:send_command(port,'RESET')
        wait(15)
    capture('baseline')
    if kind=='resume-restart':
        # Netplay ignores ordinary PAUSE_TOGGLE. Exercise the actual menu return.
        for port in ports:send_command(port,'MENU_TOGGLE')
        wait(3)
        capture('quick-menu')
        for port in ports:send_command(port,'MENU_TOGGLE')
        wait(4);capture('resumed')
        reset_all();capture('coordinated-restart')
        send_command(ports[-1],'RESET');wait(15);capture('single-peer-restart')
        reset_all();capture('recovery-restart')
    elif kind=='stall':
        peer=processes[-1]
        for seconds in (2,20):
            peer.send_signal(signal.SIGSTOP)
            try:time.sleep(seconds)
            finally:peer.send_signal(signal.SIGCONT)
            wait(5);capture(f'resumed-after-{seconds}s-stall')
            reset_all();capture(f'recovery-after-{seconds}s-stall')
    elif kind=='reconnect':
        index=len(processes)-1
        old=processes[index];old_item=asdict(results[index])
        forced=close_instance(old,ports[index]);old_item.update(exit_code=old.returncode,forced_kill=forced)
        if old.returncode!=0 or forced:raise RuntimeError('Peer did not disconnect cleanly')
        logs[index].close()
        log_path=output/(results[index].role+'-reconnected.log')
        log=log_path.open('wb');logs[index]=log
        process=subprocess.Popen(commands[index],cwd=output,stdout=log,stderr=subprocess.STDOUT)
        processes[index]=process;results[index].pid=process.pid;results[index].log=str(log_path)
        (output/'reconnect-pids.json').write_text(json.dumps({'closed':old_item,'active':[asdict(i) for i in results]},indent=2)+'\n')
        wait(20);capture('reconnected')
        reset_all();capture('reconnect-coordinated-restart')
    elif kind=='options':
        # Hold only these owned frontends while the operator uses their GUI.
        # A local JSON command records a phase, resets peers, or ends the run.
        control=output/'exercise-command.json'
        deadline=time.monotonic()+420
        (output/'options-ready.json').write_text(json.dumps({'ports':ports,'pids':[p.pid for p in processes]})+'\n')
        while time.monotonic()<deadline:
            wait(0.1)
            if not control.exists():continue
            command=json.loads(control.read_text());control.unlink()
            if command.get('reset'):reset_all()
            if command.get('phase'):
                wait(command.get('settle',3))
                capture(command['phase'],command.get('expected_link',True))
            if command.get('finish'):break
        else:raise RuntimeError('Core Options exercise reached its bounded timeout')
    failed=[p['phase'] for p in phases if p['expected_link'] and not p['native_link_ready']]
    return {'kind':kind,'phases':phases,'failed_phases':failed,
            'status':'verified' if not failed else 'needs_diagnosis'}
