#!/usr/bin/env python3
"""Compare shot-flash filtering with identical Software-core inputs and machine states.

The 96-byte Libretro presentation tail stores the tagged flash history at +76.
Emulated machine bytes must remain identical between enabled/disabled sweeps.
Outputs and frontend save data are isolated; ROMs remain external.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import runpy
import struct
api = runpy.run_path(str(Path(__file__).with_name('smoke-libretro.py')))
Game, AV, Variable = [api[k] for k in ('Game', 'AV', 'Variable')]
ENV, VIDEO, AUDIO, BATCH, POLL, STATE = [api[k] for k in ('ENV','VIDEO','AUDIO','BATCH','POLL','STATE')]
def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('core','system','rom','output'): p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--frames',type=int,default=2300)
    p.add_argument('--allow-no-flashes',action='store_true',help='For non-lightgun no-op checks')
    p.add_argument('--strict-state-replay',action='store_true',
                   help='Require exact first/repeated video replay and machine state round-trip')
    a=p.parse_args(); assert a.frames > 1100
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);(out/'saves').mkdir()
    core=C.CDLL(str(a.core.resolve()))
    core.retro_load_game.argtypes=[C.POINTER(Game)];core.retro_load_game.restype=C.c_bool
    core.retro_serialize_size.restype=C.c_size_t
    core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];core.retro_serialize.restype=C.c_bool
    core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];core.retro_unserialize.restype=C.c_bool
    paths={9:str(a.system.resolve()).encode(),31:str(out/'saves').encode()}
    options={b'sm2_renderer':b'software',b'sm2_software_renderer_threading':b'synchronous',
             b'sm2_av_timing':b'native',b'sm2_gun_input':b'analog',b'sm2_crosshairs':b'0',
             b'sm2_hide_shot_flash':b'disabled'}
    frame=0;image=b'';pcm=bytearray();shutdown=False
    @ENV
    def env(cmd,data):
        nonlocal shutdown
        if cmd in paths:C.cast(data,C.POINTER(C.c_char_p))[0]=paths[cmd];return True
        if cmd==3:C.cast(data,C.POINTER(C.c_bool))[0]=True;return True
        if cmd==10:return C.cast(data,C.POINTER(C.c_int))[0]==1
        if cmd==15:
            v=C.cast(data,C.POINTER(Variable)).contents;v.value=options.get(v.key);return v.value is not None
        if cmd==17:C.cast(data,C.POINTER(C.c_bool))[0]=False;return True
        if cmd==7:shutdown=True;return True
        return cmd in (11,18,37,60,87)
    @VIDEO
    def video(data,w,h,pitch):
        nonlocal image
        assert data and (w,h,pitch)==(496,384,496*4)
        image=C.string_at(data,h*pitch)
    @BATCH
    def batch(data,count):pcm.extend(C.string_at(data,count*4));return count
    @AUDIO
    def audio(l,r):raise AssertionError('Unexpected sample callback')
    @POLL
    def poll():pass
    @STATE
    def state(port,device,index,button):
        if port:return 0
        if device==1:
            if button==2 and (800<=frame<810 or 820<=frame<830):return 1
            if button==3 and (870<=frame<880 or 950<=frame<960 or 1050<=frame<1060):return 1
            if button==0 and frame>1100 and frame%90<2:return 1
        if device==5 and index==0 and frame>1100:
            if button==0:return -22000 if (frame//180)%2==0 else 22000
            if button==1:return -18000 if (frame//240)%2==0 else 18000
        return 0
    for name,cb in zip(('environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state'),(env,video,audio,batch,poll,state)):
        getattr(core,'retro_set_'+name).argtypes=[type(cb)];getattr(core,'retro_set_'+name)(cb)
    core.retro_init()
    try:
        game=Game(str(a.rom.resolve()).encode(),None,0,None);assert core.retro_load_game(C.byref(game))
        size=core.retro_serialize_size();assert size==9437184
        buf=C.create_string_buffer(size)
        def save():
            assert core.retro_serialize(buf,size);return buf.raw
        def load(data):
            b=C.create_string_buffer(bytes(data));assert core.retro_unserialize(b,len(data))
        def ppm(path):
            rgb=bytearray(496*384*3)
            rgb[0::3]=image[2::4];rgb[1::3]=image[1::4];rgb[2::3]=image[0::4]
            path.write_bytes(b'P6\n496 384\n255\n'+rgb)
        for frame in range(1100):core.retro_run();assert not shutdown
        baseline=save();(out/'baseline.state').write_bytes(baseline)
        results={};saved_flash=None
        for mode in ('disabled','enabled'):
            options[b'sm2_hide_shot_flash']=mode.encode();load(baseline);pcm.clear()
            images={};states={};hidden=[];replay_checked=False
            for frame in range(1100,a.frames):
                core.retro_run();assert not shutdown
                snapshot=save();states[frame]=sha(snapshot[:-96]);images[frame]=sha(image)
                flags=struct.unpack_from('<I',snapshot,size-96+76)[0]
                if flags&16:
                    assert flags&0xffff0000==0x47460000
                    hidden.append(frame)
                    if mode=='enabled' and not replay_checked:
                        saved_flash=snapshot;(out/'shot.state').write_bytes(snapshot)
                        ppm(out/'shot-filtered.ppm')
                        saved_flash_frame=frame
                        replay_checked=True
            results[mode]={'hidden_frames':hidden,'image_hashes':images,'machine_hashes':states}
            # Repeat the sweep to isolate first-replay video drift from filtering.
            options[b'sm2_hide_shot_flash']=mode.encode();load(baseline);pcm.clear()
            repeated=[];stable_images={}
            for frame in range(1100,a.frames):
                core.retro_run()
                stable_images[frame]=sha(image)
                if stable_images[frame]!=images[frame]:repeated.append(frame)
            results[mode]['repeat_video_differences']=repeated
            results[mode]['image_hashes']=stable_images
            results[mode]['audio_sha256']=sha(pcm)
        disabled,enabled=results['disabled'],results['enabled']
        assert not disabled['hidden_frames']
        assert disabled['machine_hashes']==enabled['machine_hashes'],'Filter changed emulated machine state'
        assert disabled['audio_sha256']==enabled['audio_sha256'],'Filter changed PCM'
        hidden_frames=enabled['hidden_frames']
        changed=[f for f in disabled['image_hashes'] if disabled['image_hashes'][f]!=enabled['image_hashes'][f]]
        assert hidden_frames or a.allow_no_flashes,'Input sequence did not exercise a shot flash'
        (out/'frame-trace.json').write_text(json.dumps({'hidden':hidden_frames,'changed':changed,'disabled_repeat':disabled['repeat_video_differences'],'enabled_repeat':enabled['repeat_video_differences']},indent=2)+'\n')
        assert set(changed).issubset(hidden_frames),'Video changed outside recognized shot frames'
        assert changed or a.allow_no_flashes,'Shots did not produce a visible filtering difference'
        if hidden_frames:
            options[b'sm2_hide_shot_flash']=b'disabled';load(baseline)
            for frame in range(1100,hidden_frames[0]+1):core.retro_run()
            ppm(out/'shot-normal.ppm')
        if saved_flash:
            options[b'sm2_hide_shot_flash']=b'enabled';load(saved_flash)
            assert save()==saved_flash
            future=[]
            for frame in range(saved_flash_frame+1,saved_flash_frame+4):
                core.retro_run();future.append(save())
            load(saved_flash)
            for frame,expected in zip(range(saved_flash_frame+1,saved_flash_frame+4),future):
                core.retro_run();assert save()==expected,'Replay from active flash diverged'
        # Previous cores left the presentation extension zeroed. Test that shape
        # without changing any machine or existing frontend fields.
        load(baseline);normalized_baseline=save()
        legacy=bytearray(baseline);legacy[-20:-16]=bytes(4);load(legacy)
        legacy_loaded=save();assert legacy_loaded[:-96]==normalized_baseline[:-96]
        normalized_bytes=sum(a!=b for a,b in zip(baseline[:-96],normalized_baseline[:-96]))
        if a.strict_state_replay:
            assert not any(r['repeat_video_differences'] for r in results.values()), 'First/repeated video replay differs'
            assert normalized_bytes == 0, 'Machine state changed on load'
        (out/'legacy-shaped.state').write_bytes(legacy)
        report={'game':a.rom.stem,'frames_per_sweep':a.frames-1100,
                'hidden_frames':hidden_frames,'changed_video_frames':changed,
                'first_repeat_video_differences':{m:results[m]['repeat_video_differences'] for m in results},
                'machine_bytes_identical':True,'pcm_identical':True,
                'baseline_load_normalized_machine_bytes':normalized_bytes,
                'active_flash_state_replay':bool(saved_flash),'legacy_reserved_bytes_load':True,
                'audio_sha256':enabled['audio_sha256'],'save_state_size':size}
        (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    finally:core.retro_unload_game();core.retro_deinit()
if __name__=='__main__':main()
