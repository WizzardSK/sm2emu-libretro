#!/usr/bin/env python3
"""Actual-core F05/F14 regression with consuming frontend reads and isolated saves.

ABI/transport evidence only: does not replace RetroArch menu or linked-gameplay
acceptance. Reuses smoke-libretro types and the established native patch catalog.
"""
import argparse
import ctypes as C
import importlib.util
import json
import shutil
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
    spec.loader.exec_module(mod); return mod

abi = module('network_smoke_types', HERE / 'smoke-libretro.py')
data = module('network_patch_catalog', HERE / 'test_retroarch_network_data.py')
PATCHES = data.patch_catalog(HERE.parent / 'src/libretro/nvram_settings_data.inc')
DISPLAY = C.CFUNCTYPE(C.c_bool)
SEND = C.CFUNCTYPE(None, C.c_int, C.c_void_p, C.c_size_t, C.c_uint16)
NPOLL = C.CFUNCTYPE(None)
START = C.CFUNCTYPE(None, C.c_uint16, SEND, NPOLL)
RECEIVE = C.CFUNCTYPE(None, C.c_void_p, C.c_size_t, C.c_uint16)
CONNECTED = C.CFUNCTYPE(C.c_bool, C.c_uint16)
DISCONNECTED = C.CFUNCTYPE(None, C.c_uint16)
class Net(C.Structure):
    _fields_ = [('start', START), ('receive', RECEIVE), ('stop', NPOLL), ('poll', NPOLL),
                ('connected', CONNECTED), ('disconnected', DISCONNECTED), ('version', C.c_char_p)]
class Value(C.Structure):
    _fields_ = [('value', C.c_char_p), ('label', C.c_char_p)]
class Definition(C.Structure):
    _fields_ = [(n,C.c_char_p) for n in ('key','desc','desc_category','info','info_category','category')] + [('values', Value*128),('default',C.c_char_p)]
class Options(C.Structure):
    _fields_ = [('categories',C.c_void_p),('definitions',C.POINTER(Definition))]
class Visibility(C.Structure):
    _fields_ = [('key',C.c_char_p),('visible',C.c_bool)]

class Frontend:
    def __init__(self, core, system, output, version=2, f05=False):
        self.lib=C.CDLL(str(core.resolve()));self.output=output;output.mkdir(parents=True,exist_ok=True)
        self.values={b'sm2_renderer':b'software',b'sm2_controller_profile_type':b'test_service',
                     b'sm2_nvram_settings':b'enabled' if f05 else b'disabled',b'sm2_initial_nvram_setup':b'enabled'}
        self.updated=False;self.display=None;self.net=None;self.version=version
        self.definitions={};self.visible={};self.messages=[];self.errors=[];self.reentrant=True
        assets=system/'sm2-emu' if (system/'sm2-emu').is_dir() else system
        system_copy=output/'system/sm2-emu';system_copy.mkdir(parents=True,exist_ok=True)
        for asset in assets.iterdir():
            if asset.is_file():shutil.copy2(asset,system_copy/asset.name)
        self.dirs={9:str(system_copy.parent.resolve()).encode(),31:str(output.resolve()).encode(),30:b'test'}
        @abi.ENV
        def environment(command,pointer):
            if command in self.dirs:C.cast(pointer,C.POINTER(C.c_char_p))[0]=self.dirs[command];return True
            if command==52:C.cast(pointer,C.POINTER(C.c_uint))[0]=version;return True
            if command==67:
                definitions=C.cast(pointer,C.POINTER(Options)).contents.definitions
                for d in definitions:
                    if not d.key:break
                    pairs=[]
                    for v in d.values:
                        if not v.value:break
                        pairs.append((v.value.decode(),(v.label or v.value).decode()))
                    self.definitions[d.key.decode()]={'label':d.desc.decode(),'info':(d.info or b'').decode(),'default':d.default.decode(),'choices':pairs}
                    self.values.setdefault(d.key,d.default)
                return True
            if command==16:
                for v in C.cast(pointer,C.POINTER(abi.Variable)):
                    if not v.key:break
                    label,raw=v.value.decode().split('; ',1);choices=raw.split('|')
                    self.definitions[v.key.decode()]={'label':label,'default':choices[0],'choices':[(v,v) for v in choices]}
                    self.values.setdefault(v.key,choices[0].encode())
                return True
            if command==15:
                self.updated=False  # RetroArch GET_VARIABLE consumes the global signal.
                v=C.cast(pointer,C.POINTER(abi.Variable)).contents;v.value=self.values.get(v.key);return v.value is not None
            if command==17:C.cast(pointer,C.POINTER(C.c_bool))[0]=self.updated;self.updated=False;return True
            if command==70:
                v=C.cast(pointer,C.POINTER(abi.Variable)).contents
                if self.values.get(v.key)!=v.value:self.updated=True
                self.values[v.key]=v.value
                if self.display and self.reentrant:self.display()
                return True
            if command==69:self.display=DISPLAY(C.cast(pointer,C.POINTER(C.c_void_p))[0]);return True
            if command==55:
                v=C.cast(pointer,C.POINTER(Visibility)).contents;self.visible[v.key.decode()]=v.visible;return True
            if command==78:self.net=C.cast(pointer,C.POINTER(Net)).contents;return True
            if command==59:C.cast(pointer,C.POINTER(C.c_uint))[0]=1;return True
            if command==60:self.messages.append(C.cast(pointer,C.POINTER(abi.MessageExt)).contents.msg.decode());return True
            if command==6:self.messages.append(C.cast(pointer,C.POINTER(abi.Variable)).contents.key.decode());return True
            if command==7:self.errors.append('Core requested shutdown');return True
            if command==3:C.cast(pointer,C.POINTER(C.c_bool))[0]=True;return True
            return command in (10,11,18,37,87)
        self.environment=environment
        self.last_pixels=b''
        def video(p,w,h,pitch):
            if p and (w,h,pitch)==(496,384,1984):self.last_pixels=C.string_at(p,pitch*h)
        self.video=abi.VIDEO(video);self.audio=abi.AUDIO(lambda *a:None)
        self.batch=abi.BATCH(lambda samples,n:n);self.poll=abi.POLL(lambda:None);self.input=abi.STATE(lambda *a:0)
        for name,kind in [('environment',abi.ENV),('video_refresh',abi.VIDEO),('audio_sample',abi.AUDIO),('audio_sample_batch',abi.BATCH),('input_poll',abi.POLL),('input_state',abi.STATE)]:
            getattr(self.lib,'retro_set_'+name).argtypes=[kind]
        self.lib.retro_set_environment(self.environment);self.lib.retro_set_video_refresh(self.video)
        self.lib.retro_set_audio_sample(self.audio);self.lib.retro_set_audio_sample_batch(self.batch)
        self.lib.retro_set_input_poll(self.poll);self.lib.retro_set_input_state(self.input)
        self.lib.retro_get_memory_data.argtypes=[C.c_uint];self.lib.retro_get_memory_data.restype=C.c_void_p
        self.lib.retro_get_memory_size.argtypes=[C.c_uint];self.lib.retro_get_memory_size.restype=C.c_size_t
        self.lib.retro_load_game.argtypes=[C.POINTER(abi.Game)];self.lib.retro_load_game.restype=C.c_bool
        self.lib.retro_init()
        self.send=SEND(lambda *a:None);self.netpoll=NPOLL(lambda:None)
    def set(self, values, paused=True):
        self.values.update({k.encode():v.encode() for k,v in values.items()});self.updated=True
        if paused and self.display:
            for _ in range(3):self.display()
    def run(self, count=1):
        for _ in range(count):self.lib.retro_run()
        assert not self.errors,self.errors
    def memory(self):return C.string_at(self.lib.retro_get_memory_data(0),self.lib.retro_get_memory_size(0))
    def check(self,catalog,fields):
        memory=self.memory();assert len(memory)==16576
        for suffix,value in fields.items():
            if catalog.startswith('powsled') and suffix=='ride_id':
                raw={'silver':0,'red':1,'black':2,'yellow':3}[value]
                assert all(memory[64+offset]==raw for offset in (8,264,520)),(catalog,value)
                continue
            patches,wanted=PATCHES[catalog,suffix,value]
            for (offset,mask,kind),byte in zip(patches,wanted):
                actual=memory[64+(16384 if kind=='Eeprom' else 0)+offset]
                assert actual&mask==byte&mask,(catalog,suffix,value,offset,actual,byte)
    def resets(self):return len([m for m in self.messages if 'machine reset' in m])
    def load(self,path,save=None):
        self.game=abi.Game(str(path.resolve()).encode(),None,0,None)
        assert self.lib.retro_load_game(C.byref(self.game)),path
        if save is not None:
            assert len(save)==self.lib.retro_get_memory_size(0)
            C.memmove(self.lib.retro_get_memory_data(0),save,len(save))
        self.run(2)
    def close(self):self.lib.retro_unload_game();self.lib.retro_deinit()

CASES={
 'powsledm':('powsledm',{'ride_id':'red'},{'ride_id':'silver'}),
 'powsled':('powsled',{'ride_id':'red'},{'ride_id':'silver'}),
 'daytona':('daytona',{'link_id':'master','car_number':'1'},{'link_id':'slave','car_number':'2'}),
 'daytonagtx':('daytonagtx',{'link_id':'master','car_number':'1'},{'link_id':'slave','car_number':'2'}),
 'stcc':('stcc',{'link_type':'car_1'},{'link_type':'car_2'}),
 'srallyc':('srallyc',{'link_type':'car_1'},{'link_type':'car_2'}),
 'indy500':('indy500',{'network_type':'master','cabinet_id':'1'},{'network_type':'slave','cabinet_id':'2'}),
 'motoraid':('motoraid',{'network_type':'master','cabinet_id':'1'},{'network_type':'slave','cabinet_id':'2'}),
 'waverunr':('waverunr',{'network_type':'master','cabinet_id':'1'},{'network_type':'slave','cabinet_id':'2'}),
 'skisuprg':('skisuprg',{'network_type':'master','cabinet_id':'1'},{'network_type':'slave','cabinet_id':'2'}),
 'sgt24h':('sgt24h',{'link_type':'car_no1_master','link_max':'2'},{'link_type':'car_no2_slave','link_max':'2'}),
 'overrev':('overrev',{'link_type':'master_carno_1','link_max':'2_links'},{'link_type':'slave_carno_2','link_max':'2_links'}),
 'manxtt':('manxtt',{'link_type':'master'},{'link_type':'slave'}),
 'von':('von',{'network_link_attribute':'master'},{'network_link_attribute':'slave'}),
}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--core',type=Path,required=True);parser.add_argument('--system',type=Path,required=True)
    parser.add_argument('--rom-dir',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--games',default=','.join(CASES));parser.add_argument('--f05-only',action='store_true');parser.add_argument('--boot-frames',type=int,default=0);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);reports=[]
    for version in ([] if args.boot_frames else [2] if args.f05_only else [2,0]):
        f=Frontend(args.core,args.system,args.output/f'f05-api{version}',version,True)
        try:
            f.load(args.rom_dir/'vf2.zip');before=f.resets()
            assert not any('network_board' in k for k in f.definitions)
            for key, definition in f.definitions.items():
                if key.startswith('sm2_linked_cabinets_'):
                    assert definition['label']=='Linked Cabinets'
                    assert definition['default']==('unsupported' if key.endswith('_unsupported') else '-1')
                if key.startswith('sm2_automatic_network_'):
                    assert definition['label']=='Auto Network Role Settings'
                    game=key.removeprefix('sm2_automatic_network_')
                    expected='unsupported' if game=='unsupported' else 'r' if game in ('powsledr','vonr') else '1' if game in ('powsledm','powsled') else '0'
                    assert definition['default']==expected,(version,key,definition)
            if version==2:
                assert f.visible['sm2_linked_cabinets_unsupported']
                assert f.visible['sm2_automatic_network_unsupported']
                assert sum(v for k,v in f.visible.items() if k.startswith('sm2_linked_cabinets_'))==1
                assert sum(v for k,v in f.visible.items() if k.startswith('sm2_automatic_network_'))==1
            f.set({'sm2_nvram_vf2_difficulty':'hard'});f.run();f.check('vf2',{'difficulty':'hard'})
            assert f.resets()==before+1,(version,f.messages)
            f.run(3);assert f.resets()==before+1
            reports.append({'scope':'F05','api':version,'consuming_reads':True,'paused_callback':bool(f.display),'one_reset':True,'reentrant_publication':True})
        finally:f.close()
    if not args.f05_only:
        for game in args.games.split(','):
            catalog,master,slave=CASES[game];f=Frontend(args.core,args.system,args.output/game)
            try:
                f.load(args.rom_dir/(game+'.zip'));assert f.net
                if args.boot_frames:
                    f.run(args.boot_frames)
                    pixels=f.last_pixels;rgb=bytearray(len(pixels)//4*3);rgb[0::3]=pixels[2::4];rgb[1::3]=pixels[1::4];rgb[2::3]=pixels[0::4]
                    (args.output/(game+'.ppm')).write_bytes(b'P6\n496 384\n255\n'+rgb)
                    reports.append({'scope':'boot','game':game,'frames':args.boot_frames,'clean_exit':True});print(game,'BOOT',flush=True);continue
                key='sm2_automatic_network_'+game;linked='sm2_linked_cabinets_'+game
                assert f.visible[key] and f.visible[linked]
                f.net.start(0,f.send,f.netpoll);assert f.net.connected(1)
                first='2' if game.startswith('powsled') else '1';second='1' if game.startswith('powsled') else '2'
                start=f.resets();f.set({key:first});f.run();f.check(catalog,master);assert f.resets()==start+1,(game,'master',f.messages)
                for suffix,value in master.items():assert f.values[('sm2_nvram_'+catalog+'_'+suffix).encode()]==value.encode()
                f.run(3);assert f.resets()==start+1,(game,'unchanged')
                start=f.resets();f.set({linked:'2',key:second});f.run();f.check(catalog,slave);assert f.resets()==start+1,(game,'combined',f.messages)
                start=f.resets();f.set({linked:'-1'});f.run();f.check(catalog,slave);assert f.resets()==start+1,(game,'independence')
                start=f.resets();f.set({key:'-1','sm2_nvram_settings':'enabled'});f.run();f.check(catalog,slave);assert f.resets()==start,(game,'handover',f.messages)
                for suffix,value in slave.items():assert f.values[('sm2_nvram_'+catalog+'_'+suffix).encode()]==value.encode()
                start=f.resets();f.set({linked:'0'});f.run();assert f.resets()==start,(game,'alias')
                f.lib.retro_reset();f.run();f.check(catalog,slave)
                assert f.net.connected(2),(game,'lobby clients lost')
                f.net.stop()
                retained=f.memory()
                reports.append({'scope':'F14','game':game,'nvram_off_authority':True,'role_topology_independent':True,'last_applied_handover':True,'combined_reset':True,'unchanged_alias':True,'lobby_callbacks_retained':True})
                print(game,'PASS',flush=True)
            finally:f.close()
            if not args.boot_frames:
                reload=Frontend(args.core,args.system,args.output/(game+'-reload'))
                try:
                    reload.values[('sm2_automatic_network_'+game).encode()]=b'-1'
                    reload.load(args.rom_dir/(game+'.zip'),retained)
                    reload.check(catalog,slave)
                    reports[-1]['fresh_reload_with_manual_authority']=True
                finally:reload.close()
    (args.output/'results.json').write_text(json.dumps(reports,indent=2)+'\n');print('F05/F14 checks passed:',len(reports))
if __name__=='__main__':main()
