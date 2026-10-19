#!/usr/bin/env python3
"""Exercise the OpenGL ES core through a minimal surfaceless EGL frontend."""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import time
import wave

api=runpy.run_path(str(Path(__file__).with_name('smoke-libretro.py')))
Game,AV,Variable,MessageExt=[api[x] for x in ['Game','AV','Variable','MessageExt']]
ENV,VIDEO,AUDIO,BATCH,POLL,STATE=[api[x] for x in ['ENV','VIDEO','AUDIO','BATCH','POLL','STATE']]
def sha(data):return hashlib.sha256(data).hexdigest()
def files(path):return {str(p.relative_to(path)):sha(p.read_bytes()) for p in sorted(path.rglob('*')) if p.is_file()}

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
    p.add_argument('--api',choices=['gles','desktop'],default='gles')
    p.add_argument('--hide-shot-flash',choices=['disabled','enabled'],default='disabled')
    p.add_argument('--gun-inputs',action='store_true',help='Replay coin, start, aim and lightgun shots')
    p.add_argument('--crosshairs', choices=['auto','0','1','2','3'])
    p.add_argument('--crosshair-style', choices=['sm2','supermodel','auto','custom'], default='sm2')
    p.add_argument('--crosshair-timeout', choices=['disabled','1','2','3','4','5','6','7','8','10','15','30','60'], default='disabled')
    p.add_argument('--scale',type=int,choices=range(1,9),default=1)
    p.add_argument('--texture-filter',choices=['faithful','2','4','8','16'],default='faithful')
    p.add_argument('--upscale-2d',choices=['faithful','xbr','scalefx'],default='faithful')
    p.add_argument('--context-cycle',type=int,default=0)
    p.add_argument('--context-loss-cycle',type=int,default=0)
    p.add_argument('--av-timing',choices=['native','60hz'],default='native')
    p.add_argument('--timing-overlay',choices=['disabled','auto','11','12','13','14'],default='disabled')
    p.add_argument('--reference',type=Path)
    p.add_argument('--exercise',action='store_true')
    a=p.parse_args();assert a.frames>0 and not(a.context_cycle and a.context_loss_cycle)
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);(out/'saves').mkdir()
    host=C.CDLL(str(a.host.resolve()));core=C.CDLL(str(a.core.resolve()))
    host.sm2_gl_set_es.argtypes=[C.c_bool];host.sm2_gl_set_es(a.api=='gles')
    host.sm2_gl_environment.argtypes=[C.c_uint,C.c_void_p];host.sm2_gl_environment.restype=C.c_bool
    host.sm2_gl_start.restype=C.c_bool;host.sm2_gl_error.restype=C.c_char_p
    host.sm2_gl_frame.argtypes=[C.c_uint,C.c_uint,C.c_bool];host.sm2_gl_frame.restype=C.c_bool
    host.sm2_gl_pixels.restype=C.c_void_p
    core.retro_load_game.argtypes=[C.POINTER(Game)];core.retro_load_game.restype=C.c_bool
    core.retro_get_system_av_info.argtypes=[C.POINTER(AV)]
    paths={9:str(a.system.resolve()).encode(),31:str(out/'saves').encode()}
    options={b'sm2_aspect_ratio':a.aspect_ratio.encode(),
             b'sm2_widescreen_mode':a.widescreen_mode.encode(),b'sm2_hide_shot_flash':a.hide_shot_flash.encode(),
             b'sm2_gun_input':b'analog' if a.gun_inputs else b'hybrid',b'sm2_crosshairs':a.crosshairs.encode() if a.crosshairs else (b'0' if a.gun_inputs else b'auto'),
             b'sm2_crosshair_style':a.crosshair_style.encode(),b'sm2_crosshair_timeout':a.crosshair_timeout.encode(),
             b'sm2_renderer':b'opengl',b'sm2_internal_resolution':str(a.scale).encode(),
             b'sm2_texture_filter':a.texture_filter.encode(),b'sm2_upscale_2d':a.upscale_2d.encode(),
             b'sm2_initial_nvram_setup':a.initial_nvram_setup.encode(),
             b'sm2_av_timing':a.av_timing.encode(),b'sm2_timing_overlay':a.timing_overlay.encode()}
    shutdown=False;errors=[];pcm=bytearray();last=b'';frame=0;videos=0;gl_frames=0;duplicates=0
    statuses=[];cycle_hardware_frame=None
    @ENV
    def env(cmd,data):
        nonlocal shutdown
        if cmd in paths:C.cast(data,C.POINTER(C.c_char_p))[0]=paths[cmd];return True
        if cmd==3:C.cast(data,C.POINTER(C.c_bool))[0]=True;return True
        if cmd==15:
            var=C.cast(data,C.POINTER(Variable)).contents
            var.value=options.get(var.key);return var.value is not None
        if cmd==17:C.cast(data,C.POINTER(C.c_bool))[0]=False;return True
        if cmd==60:statuses.append(C.cast(data,C.POINTER(MessageExt)).contents.msg.decode());return True
        if cmd==7:shutdown=True;return True
        if cmd in [10,11,16,18]:return True
        return host.sm2_gl_environment(cmd,data)
    @VIDEO
    def video(data,w,h,pitch):
        nonlocal last,videos,gl_frames,duplicates,cycle_hardware_frame
        videos+=1
        if not data:
            duplicates+=1
            if (a.context_cycle or a.context_loss_cycle) and frame in (a.context_cycle,a.context_loss_cycle):
                cycle_hardware_frame=False
            return
        if data!=C.c_void_p(-1).value or (w,h,pitch)!=((a.expect_width if not a.widescreen_switch_frame or frame >= a.widescreen_switch_frame else (496 if a.expect_width == 662 else 662))*a.scale,384*a.scale,0):
            errors.append('Invalid hardware frame');return
        if (a.context_cycle or a.context_loss_cycle) and frame in (a.context_cycle,a.context_loss_cycle):
            cycle_hardware_frame=True
        capture=frame>=a.frames-2
        if not host.sm2_gl_frame(w,h,capture):errors.append(host.sm2_gl_error().decode());return
        if capture:
            rgba=C.string_at(host.sm2_gl_pixels(),w*h*4)
            rows=[rgba[y*w*4:(y+1)*w*4] for y in range(h-1,-1,-1)]
            rgba=b''.join(rows)
            rgb=bytearray(w*h*3);rgb[0::3]=rgba[0::4];rgb[1::3]=rgba[1::4];rgb[2::3]=rgba[2::4]
            last=f'P6\n{w} {h}\n255\n'.encode()+rgb
        gl_frames+=1
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
    callbacks=[env,video,sample,audio,poll,state]
    for name,cb in zip(['environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state'],callbacks):
        getattr(core,'retro_set_'+name).argtypes=[type(cb)];getattr(core,'retro_set_'+name)(cb)
    game=Game(str(a.rom.resolve()).encode(),None,0,None)
    core.retro_init();assert core.retro_load_game(C.byref(game))
    assert host.sm2_gl_start(),host.sm2_gl_error()
    av=AV();core.retro_get_system_av_info(C.byref(av));native_fps=25000000/434600
    assert abs(av.timing.fps-(60 if a.av_timing!='native' else native_fps))<1e-9
    started=time.monotonic()
    for frame in range(a.frames):
        if a.widescreen_switch_frame and frame == a.widescreen_switch_frame:
            options[b'sm2_widescreen_mode'] = b'expand_3d' if a.widescreen_mode == 'stretch' else b'stretch'
        if a.context_cycle and frame==a.context_cycle:
            host.sm2_gl_stop();assert host.sm2_gl_start(),host.sm2_gl_error()
        if a.context_loss_cycle and frame==a.context_loss_cycle:
            host.sm2_gl_lose_context();assert host.sm2_gl_start(),host.sm2_gl_error()
        core.retro_run();assert not shutdown and not errors,(frame,errors)
    elapsed=time.monotonic()-started
    assert videos==a.frames and last
    assert duplicates==0
    if a.av_timing=='60hz':
        assert abs(len(pcm)//4-a.frames*av.timing.rate/60)<av.timing.rate/native_fps+2
    overlays=[entry for entry in statuses if entry]
    if a.timing_overlay!='disabled':assert not overlays
    if a.context_cycle or a.context_loss_cycle:assert cycle_hardware_frame is True
    core.retro_get_system_av_info(C.byref(av))
    assert av.geometry.width == a.expect_width * a.scale
    if a.expect_aspect:
        expected_aspect = 16/9 if a.expect_aspect == '16:9' else 4/3
        assert abs(av.geometry.aspect - expected_aspect) < 1e-6
    (out/'native_frame.ppm').write_bytes(last)
    with wave.open(str(out/'audio.wav'),'wb') as wav:
        wav.setparams((2,2,int(av.timing.rate),0,'NONE','none'));wav.writeframes(pcm)
    nvram=api['capture_save_ram'](core,a.rom.stem,out/'saves')
    host.sm2_gl_stop();core.retro_unload_game();shutil.copytree(out/'saves',out/'baseline-nvram')
    report={'hide_shot_flash':a.hide_shot_flash,'gun_inputs':a.gun_inputs,'initial_nvram_setup':a.initial_nvram_setup,'frames':a.frames,'gl_frames':gl_frames,'duplicated_frames':duplicates,'api':a.api,'crosshairs':a.crosshairs,'crosshair_style':a.crosshair_style,'crosshair_timeout':a.crosshair_timeout,
        'aspect_ratio':a.aspect_ratio,'widescreen_mode':a.widescreen_mode,
        'expected_width':a.expect_width,'widescreen_switch_frame':a.widescreen_switch_frame,'scale':a.scale,
        'texture_filter':a.texture_filter,'upscale_2d':a.upscale_2d,
        'av_timing':a.av_timing,'timing_overlay':a.timing_overlay,'overlay_updates':len(overlays),
        'context_cycle':a.context_cycle,'context_loss_cycle':a.context_loss_cycle,
        'cycle_hardware_frame':cycle_hardware_frame,'gpu_seconds':elapsed,'audio_frames':len(pcm)//4,
        'video_sha256':sha(last),'audio_sha256':sha(pcm),'nvram':nvram}
    if a.reference:
        expected=json.loads((a.reference/'result.json').read_text())
        report['comparison']={key:report[key]==expected[key] for key in ['video_sha256','audio_sha256','nvram']}
        assert all(report['comparison'].values()),report
    if a.exercise:
        for cycle in range(3):
            assert core.retro_load_game(C.byref(game));assert host.sm2_gl_start(),host.sm2_gl_error()
            for frame in range(120):core.retro_run()
            core.retro_reset()
            for frame in range(120):core.retro_run()
            assert not shutdown and not errors,errors
            if cycle%2:core.retro_unload_game();host.sm2_gl_stop()
            else:host.sm2_gl_stop();core.retro_unload_game()
        report['load_reset_unload_cycles']=3
    core.retro_deinit();(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
