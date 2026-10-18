#!/usr/bin/env python3
"""Exercise the Vulkan core through a minimal real-GPU frontend, with native readback.

The host serializes GPU work for deterministic captures. RetroArch tests separately
cover asynchronous presentation. ROMs stay external; outputs must be new.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import time
import wave
api = runpy.run_path(str(Path(__file__).with_name('smoke-libretro.py')))
Game, AV, MessageExt = api['Game'], api['AV'], api['MessageExt']
ENV, VIDEO, AUDIO, BATCH, POLL, STATE = [api[x] for x in ['ENV','VIDEO','AUDIO','BATCH','POLL','STATE']]
class Variable(C.Structure):
    _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]
def sha(data): return hashlib.sha256(data).hexdigest()
def files(path): return {str(p.relative_to(path)):sha(p.read_bytes()) for p in sorted(path.rglob('*')) if p.is_file()}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['core','host','system','rom','output']:p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--frames',type=int,default=1800)
    p.add_argument('--aspect-ratio', choices=['auto','4_3','16_9'], default='auto')
    p.add_argument('--widescreen-mode', choices=['stretch','expand_3d'], default='stretch')
    p.add_argument('--expect-width', type=int, default=496, help='Expected native framebuffer width')
    p.add_argument('--expect-aspect', choices=['4:3','16:9'], help='Verify the final reported display aspect')
    p.add_argument('--widescreen-switch-frame', type=int, default=0,
                   help='Switch Stretch to Expand or vice versa at this frame')
    p.add_argument('--initial-nvram-setup',choices=['enabled','disabled'],default='enabled')
    p.add_argument('--hide-shot-flash',choices=['disabled','enabled'],default='disabled')
    p.add_argument('--gun-inputs',action='store_true',help='Replay coin, start, aim and lightgun shots')
    p.add_argument('--scale',type=int,choices=range(1,9),default=1)
    p.add_argument('--texture-filter',choices=['faithful','2','4','8','16'],default='faithful')
    p.add_argument('--upscale-2d',choices=['faithful','xbr','scalefx'],default='faithful')
    p.add_argument('--context-cycle',type=int,default=0,help='Destroy/recreate the real device before this frame')
    p.add_argument('--av-timing',choices=['native','60hz'],default='native')
    p.add_argument('--timing-overlay',choices=['disabled','auto','11','12','13','14'],default='disabled')
    p.add_argument('--reference',type=Path,help='Another run of this script; require exact final image and PCM')
    p.add_argument('--exercise',action='store_true',help='Additional reset/load/unload cycles')
    p.add_argument('--save-state-test',action='store_true',help='Compare an eight-frame GPU/PCM Save State round-trip')
    a=p.parse_args();assert a.frames>0
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);(out/'saves').mkdir()
    host=C.CDLL(str(a.host.resolve()));core=C.CDLL(str(a.core.resolve()))
    host.sm2_gpu_environment.argtypes=[C.c_uint,C.c_void_p];host.sm2_gpu_environment.restype=C.c_bool
    host.sm2_gpu_start.restype=C.c_bool;host.sm2_gpu_error.restype=C.c_char_p
    host.sm2_gpu_frame.argtypes=[C.c_uint,C.c_uint,C.c_bool];host.sm2_gpu_frame.restype=C.c_bool
    host.sm2_gpu_pixels.restype=C.c_void_p
    core.retro_load_game.argtypes=[C.POINTER(Game)];core.retro_load_game.restype=C.c_bool
    core.retro_get_system_av_info.argtypes=[C.POINTER(AV)]
    paths={9:str(a.system.resolve()).encode(),31:str(out/'saves').encode()}
    options={b'sm2_aspect_ratio':a.aspect_ratio.encode(),
             b'sm2_widescreen_mode':a.widescreen_mode.encode(),b'sm2_hide_shot_flash':a.hide_shot_flash.encode(),
             b'sm2_gun_input':b'analog' if a.gun_inputs else b'hybrid',b'sm2_crosshairs':b'0' if a.gun_inputs else b'auto',
             b'sm2_renderer':b'vulkan',b'sm2_internal_resolution':str(a.scale).encode(),
             b'sm2_texture_filter':a.texture_filter.encode(),b'sm2_upscale_2d':a.upscale_2d.encode(),
             b'sm2_initial_nvram_setup':a.initial_nvram_setup.encode(),
             b'sm2_av_timing':a.av_timing.encode(),b'sm2_timing_overlay':a.timing_overlay.encode()}
    shutdown=False;errors=[];pcm=bytearray();last=b'';frame=0;videos=0;gpu_frames=0;duplicates=0
    statuses=[];context_cycle_hardware_frame=None
    @ENV
    def env(cmd,data):
        nonlocal shutdown
        if cmd in paths:C.cast(data,C.POINTER(C.c_char_p))[0]=paths[cmd];return True
        if cmd==3:C.cast(data,C.POINTER(C.c_bool))[0]=True;return True
        if cmd==15:
            v=C.cast(data,C.POINTER(Variable)).contents
            if v.key in options:v.value=options[v.key];return True
        if cmd==17:C.cast(data,C.POINTER(C.c_bool))[0]=False;return True
        if cmd==60:statuses.append(C.cast(data,C.POINTER(MessageExt)).contents.msg.decode());return True
        if cmd==7:shutdown=True;return True
        if cmd in [10,11,16,18]:return True
        return host.sm2_gpu_environment(cmd,data)
    @VIDEO
    def video(data,w,h,pitch):
        nonlocal last,videos,gpu_frames,duplicates,context_cycle_hardware_frame
        videos+=1
        if not data:
            duplicates+=1
            if a.context_cycle and frame==a.context_cycle:context_cycle_hardware_frame=False
            return
        if data!=C.c_void_p(-1).value or (w,h,pitch)!=((a.expect_width if not a.widescreen_switch_frame or frame >= a.widescreen_switch_frame else (496 if a.expect_width == 662 else 662))*a.scale,384*a.scale,0):
            errors.append('Invalid hardware frame');return
        if a.context_cycle and frame==a.context_cycle:context_cycle_hardware_frame=True
        # Capture the final two frames to retain the last presented image.
        capture=frame>=a.frames-2
        if not host.sm2_gpu_frame(w,h,capture):errors.append(host.sm2_gpu_error().decode());return
        if capture:
            rgba=C.string_at(host.sm2_gpu_pixels(),w*h*4)
            rgb=bytearray(w*h*3);rgb[0::3]=rgba[0::4];rgb[1::3]=rgba[1::4];rgb[2::3]=rgba[2::4]
            last=f'P6\n{w} {h}\n255\n'.encode()+rgb
        gpu_frames+=1
    @BATCH
    def audio(data,count):pcm.extend(C.string_at(data,count*4));return count
    @AUDIO
    def sample(l,r):raise AssertionError('Unexpected per-sample callback')
    @POLL
    def poll():pass
    @STATE
    def state(port,device,index,button):
        if not a.gun_inputs or port: return 0
        if device == 1:
            if button == 2 and (800 <= frame < 810 or 820 <= frame < 830): return 1
            if button == 3 and (870 <= frame < 880 or 950 <= frame < 960 or 1050 <= frame < 1060): return 1
            if button == 0 and frame > 1100 and frame % 90 < 2: return 1
        if device == 5 and index == 0 and frame > 1100:
            if button == 0: return -22000 if (frame//180)%2 == 0 else 22000
            if button == 1: return -18000 if (frame//240)%2 == 0 else 18000
        return 0
    for name,cb in [('environment',env),('video_refresh',video),('audio_sample',sample),('audio_sample_batch',audio),('input_poll',poll),('input_state',state)]:
        getattr(core,'retro_set_'+name).argtypes=[type(cb)];getattr(core,'retro_set_'+name)(cb)
    game=Game(str(a.rom.resolve()).encode(),None,0,None)
    core.retro_init();assert core.retro_load_game(C.byref(game))
    assert host.sm2_gpu_start(),host.sm2_gpu_error()
    assert not shutdown
    av=AV();core.retro_get_system_av_info(C.byref(av))
    native_fps=25000000/434600
    assert abs(av.timing.fps-(60.0 if a.av_timing!='native' else native_fps))<1e-9
    started=time.monotonic()
    for frame in range(a.frames):
        if a.widescreen_switch_frame and frame == a.widescreen_switch_frame:
            options[b'sm2_widescreen_mode'] = b'expand_3d' if a.widescreen_mode == 'stretch' else b'stretch'
        if a.context_cycle and frame==a.context_cycle:
            host.sm2_gpu_stop();assert host.sm2_gpu_start(),host.sm2_gpu_error()
        if frame==a.frames//2:host.sm2_gpu_set_mask(15)
        if frame==a.frames*3//4:host.sm2_gpu_set_mask(7)
        core.retro_run();assert not shutdown and not errors,(frame,errors)
    elapsed=time.monotonic()-started
    assert videos==a.frames and last
    assert duplicates==0
    if a.av_timing=='60hz':
        assert abs(len(pcm)//4-a.frames*av.timing.rate/60)<av.timing.rate/native_fps+2
    overlays=[entry for entry in statuses if entry]
    if a.timing_overlay!='disabled':assert not overlays
    if a.context_cycle:assert context_cycle_hardware_frame is True
    state_roundtrip = None
    if a.save_state_test:
        core.retro_serialize_size.restype = C.c_size_t
        core.retro_serialize.argtypes = [C.c_void_p, C.c_size_t]
        core.retro_serialize.restype = C.c_bool
        core.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]
        core.retro_unserialize.restype = C.c_bool
        size = core.retro_serialize_size()
        snapshot = C.create_string_buffer(size)
        assert core.retro_serialize(snapshot, size)
        original_last, original_pcm = last, len(pcm)
        for frame in range(a.frames, a.frames + 8):
            core.retro_run()
        first_image, first_pcm = last, bytes(pcm[original_pcm:])
        assert core.retro_unserialize(snapshot, size)
        del pcm[original_pcm:]
        for frame in range(a.frames, a.frames + 8):
            core.retro_run()
        state_roundtrip = {'image': last == first_image, 'pcm': bytes(pcm[original_pcm:]) == first_pcm}
        assert all(state_roundtrip.values()) and not errors, (state_roundtrip, errors)
        last = original_last
        del pcm[original_pcm:]
    core.retro_get_system_av_info(C.byref(av))
    assert av.geometry.width == a.expect_width * a.scale
    if a.expect_aspect:
        expected_aspect = 16/9 if a.expect_aspect == '16:9' else 4/3
        assert abs(av.geometry.aspect - expected_aspect) < 1e-6
    (out/'native_frame.ppm').write_bytes(last)
    with wave.open(str(out/'audio.wav'),'wb') as w:
        w.setparams((2,2,int(av.timing.rate),0,'NONE','none'));w.writeframes(pcm)
    nvram=api['capture_save_ram'](core,a.rom.stem,out/'saves')
    host.sm2_gpu_stop();core.retro_unload_game()
    shutil.copytree(out/'saves',out/'baseline-nvram')
    report={'hide_shot_flash':a.hide_shot_flash,'gun_inputs':a.gun_inputs,'initial_nvram_setup':a.initial_nvram_setup,'frames':a.frames,'gpu_frames':gpu_frames,'duplicated_frames':duplicates,
        'aspect_ratio':a.aspect_ratio,'widescreen_mode':a.widescreen_mode,
        'expected_width':a.expect_width,'widescreen_switch_frame':a.widescreen_switch_frame,'scale':a.scale,'texture_filter':a.texture_filter,'upscale_2d':a.upscale_2d,
        'av_timing':a.av_timing,'timing_overlay':a.timing_overlay,
        'overlay_updates':len(overlays),'context_cycle':a.context_cycle,
        'context_cycle_hardware_frame':context_cycle_hardware_frame,'state_roundtrip':state_roundtrip,'sync_masks':[7,15,7],
        'gpu_seconds':elapsed,'audio_frames':len(pcm)//4,
        'video_sha256':sha(last),'audio_sha256':sha(pcm),'nvram':nvram}
    if a.reference:
        expected=json.loads((a.reference/'result.json').read_text())
        report['comparison']={key:report[key]==expected[key] for key in ['video_sha256','audio_sha256','nvram']}
        assert all(report['comparison'].values()),report
    if a.exercise:
        for cycle in range(3):
            assert core.retro_load_game(C.byref(game))
            assert host.sm2_gpu_start(),host.sm2_gpu_error()
            for frame in range(120):core.retro_run()
            core.retro_reset()
            for frame in range(120):core.retro_run()
            assert not shutdown and not errors,errors
            # Exercise both legal teardown orders while the device is alive.
            if cycle%2:core.retro_unload_game();host.sm2_gpu_stop()
            else:host.sm2_gpu_stop();core.retro_unload_game()
        report['load_reset_unload_cycles']=3
    core.retro_deinit();(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
