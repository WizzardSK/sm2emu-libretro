"""Reviewed native network choices and generated NVRAM patch metadata."""
import re
import importlib.util
from pathlib import Path
import sys

_spec=importlib.util.spec_from_file_location('retroarch_netpacket',Path(__file__).with_name('test-retroarch-netpacket.py'))
_runner=importlib.util.module_from_spec(_spec)
sys.modules[_spec.name]=_runner
_spec.loader.exec_module(_runner)
GAME_SPECS=_runner.GAME_SPECS

CASES=[{'name':game+'-'+str(count)+('-relay' if relay else ''),'game':game,'count':count,'relay':relay}
       for game,count,relay in [
           ('daytona',2,False),('daytonas',2,False),
           ('stcc',3,True),('stcca',2,False),('stccb',2,False),('stcco',2,False),
           ('srallyc',3,True),('indy500',2,False),('indy500d',2,False),
           ('motoraid',3,True),('motoraiddx',3,True),('waverunr',2,False),
           ('skisuprg',2,False),('sgt24h',2,False),('overrev',4,False),
           ('manxtt',3,False),('manxttc',3,False),('von',3,False),
           ('daytona',8,False),('stcc',9,False),('srallyc',5,False)]]


def expected_fields(case,index):
    game=case['game'];spec=GAME_SPECS[game];catalog=spec.nvram_game
    count=case['count'];number=index+1
    relay=(case['relay'] and index==count-1) or (catalog=='manxtt' and index==2)
    if spec.nvram_scheme=='car' and number==spec.max_cabinets:relay=True
    role='master' if index==0 else 'slave'
    if spec.nvram_scheme=='daytona':return {(catalog,'link_id'):role,(catalog,'car_number'):str(number)}
    if spec.nvram_scheme=='car':return {(catalog,'link_type'):'relay' if relay else f'car_{number}'}
    if spec.nvram_scheme=='role_id':
        result={(catalog,'network_type'):'live' if relay else role,(catalog,'cabinet_id'):str(number)}
        if catalog=='motoraiddx':result[catalog,'cabinet_type']='twin'
        return result
    if spec.nvram_scheme=='link_role':return {(catalog,'link_type'):'relay' if relay else role}
    if spec.nvram_scheme=='sgt24h':
        result={(catalog,'link_type'):f'car_no{number}_{role}'}
        if index==0:result[catalog,'link_max']=str(count)
        return result
    if spec.nvram_scheme=='overrev':return {(catalog,'link_type'):f'{role}_carno_{number}',(catalog,'link_max'):f'{count}_links'}
    if spec.nvram_scheme=='network_attribute':return {(catalog,'network_link_attribute'):'no_link' if index==2 else role}
    raise RuntimeError('Unsupported preset scheme: '+spec.nvram_scheme)


def patch_catalog(path):
    source=path.read_text();arrays={};patches={};values={};result={}
    for name,body in re.findall(r'static constexpr u8 (kDesired\d+)\[\] = \{(.*?)\n\};',source,re.S):
        arrays[name]=bytes(int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',body))
    for name,body in re.findall(r'static constexpr Patch (k\w*Patches\d+)\[\] = \{(.*?)\n\};',source,re.S):
        patches[name]=[(int(offset,0),int(mask,0),kind or 'BackupRam') for offset,mask,kind in re.findall(
            r'\{(0x[0-9a-fA-F]+|\d+), (0x[0-9a-fA-F]+|\d+)(?:, MemoryKind::(\w+))?\}',body)]
    for name,body in re.findall(r'static constexpr Value (kValues\d+)\[\] = \{(.*?)\n\};',source,re.S):
        values[name]={key:(desired,int(offset)) for key,desired,offset in re.findall(
            r'\{"([^"]+)", "[^"]*", (kDesired\d+) \+ (\d+)\}',body)}
    for line in source.splitlines():
        match=re.match(r'\s*\{"([^"]+)", "([^"]+)", .*?, (kValues\d+), std::size\(\3\), (k\w*Patches\d+),',line)
        if not match:continue
        game,suffix,vname,pname=match.groups();target=patches[pname]
        for key,(desired,offset) in values[vname].items():
            result[game,suffix,key]=(target,arrays[desired][offset:offset+len(target)])
    return result
