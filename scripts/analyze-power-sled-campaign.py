#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import argparse,json,hashlib
parser=argparse.ArgumentParser(description='Decode documented Power Sled native-font time screenshots; Pillow required.')
parser.add_argument('evidence',type=Path)
args=parser.parse_args()
root=args.evidence.resolve()
def glyph(path,x,y):
 im=Image.open(path).convert('RGB')
 return tuple(1 if im.getpixel((xx,yy))[0]>180 and im.getpixel((xx,yy))[1]>180 else 0 for yy in range(y,y+14) for xx in range(x,x+8))
ref=root/'mame-time0-range/1-powsledm'
training={str(n%10):ref/f'screen-{n-2:04}.png' for n in range(5,15)}
# Units always occupy x=296..303, rows y=68..81.
templates={glyph(p,296,68):digit for digit,p in training.items()}
assert len(templates)==10
blank=(0,)*112
def read_time(path,index):
 digits=[]
 for x in [264,272,280,288,296]:
  g=glyph(path,x,68+16*index)
  if g==blank:digits.append(' ')
  else:
   assert g in templates,(str(path),x,index,'unrecognized glyph')
   digits.append(templates[g])
 return int(''.join(digits).strip())
records={}
for index in range(5):
 folder=root/f'mame-time{index}-range'
 if not (folder/'manifest.json').exists():continue
 plan=json.loads((folder/'manifest.json').read_text())['plan']
 fields={}
 for unit in plan:
  shots=[folder/unit/f'screen-{i+1:04}.png' for i in range(len(plan[unit]['labels']))]
  values={label:read_time(path,index) for label,path in zip(plan[unit]['labels'],shots)}
  steps=[values[f'increase-{i:03}'] for i in range(1,112)]
  assert values['use-default']==[49,35,35,30,30][index]
  assert values['lower-bound']==5 and steps==[min(5+i,99) for i in range(1,112)]
  print(index,unit,'default',values['use-default'],'lower',values['lower-bound'],'upper',steps[-1],'distinct',len(set(steps)))
  fields[unit]={'values':values,'screenshots':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in shots}}
 records[f'checkpoint_{index}']=fields
(root/'decoded-time-values.json').write_text(json.dumps({'method':'Exact native-font glyph matching, trained on visually reviewed screen values 5 through 14','training':{digit:str(p.relative_to(root)) for digit,p in training.items()},'fields':records},indent=2)+'\n')

committed={}
for index in range(5):
 folder=root/f'mame-time{index}-commits'
 if not (folder/'manifest.json').exists():continue
 manifest=json.loads((folder/'manifest.json').read_text())
 if manifest.get('cancelled_after_user_scope_change'):continue
 assert all(u['returncode']==0 and u['probe_ok'] for u in manifest['units'])
 units={}
 for unit,plan in manifest['plan'].items():
  backups=[folder/unit/f'backup-{i:04}.bin' for i in range(1,96)]
  pictures=[folder/unit/f'screen-{i:04}.png' for i in range(1,96)]
  actual=[read_time(p,index) for p in pictures]
  assert actual==list(range(5,100)),(index,unit,actual)
  samples=[p.read_bytes() for p in backups]
  assert all(len(b)==0x4000 for b in samples)
  changed=[i for i,(a,b) in enumerate(zip(samples[0],samples[1])) if a!=b]
  assert len(changed)==3 and changed==[changed[0],changed[0]+0x100,changed[0]+0x200]
  for value,sample in zip(actual,samples):
   assert all(int.from_bytes(sample[x:x+2],'little')==value for x in changed)
   assert all(a==b for i,(a,b) in enumerate(zip(samples[0],sample)) if i not in changed)
  game=unit.split('-',1)[1]
  assert samples[-1]==(folder/unit/'nvram'/game/'backup1').read_bytes(),(unit,index,'memory dump differs from native NVRAM file')
  eeprom=folder/unit/'nvram'/game/'eeprom'
  assert eeprom.read_bytes()==bytes([255])*128
  units[unit]={'count':95,'values':actual,'offsets':changed,'encoding':'u16 little endian, three copies spaced 0x100 bytes','native_file_matches_last_dump':True,'eeprom':'unchanged all-FF 128-byte image','samples':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in backups},'screenshots':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in pictures}}
  print('commits',index,unit,'95 native commits; offsets',changed)
 committed[f'checkpoint_{index}']=units
(root/'committed-time-values.json').write_text(json.dumps({'fields':committed,'limits':'Native operator commits and byte mapping; fresh-process reload audited separately'},indent=2)+'\n')

# Motion uses the same native digit glyphs; the decimal point is fixed at x=248.
def read_motion(path):
 digits=[]
 for x in [232,240,256]:
  g=glyph(path,x,172)
  assert g in templates,(str(path),x,'unrecognized motion glyph')
  digits.append(templates[g])
 return int(''.join(digits))
folder=root/'mame-motion-range'
manifest=json.loads((folder/'manifest.json').read_text())
motion={}
for unit,plan in manifest['plan'].items():
 assert all(u['returncode']==0 and u['probe_ok'] for u in manifest['units'])
 pictures=[folder/unit/f'screen-{i+1:04}.png' for i in range(len(plan['labels'])-1)]
 values={label:read_motion(path) for label,path in zip(plan['labels'],pictures)}
 steps=[values[f'increase-{i:03}'] for i in range(1,112)]
 assert values['use-default']==380 and values['lower-bound']==100
 assert steps==[min(100+5*i,450) for i in range(1,112)]
 b=(folder/unit/'nvram'/unit.split('-',1)[1]/'backup1').read_bytes()
 assert all(int.from_bytes(b[o:o+2],'little')==450 for o in [0x1a,0x11a,0x21a])
 motion[unit]={'values_in_tenths':values,'screenshots':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in pictures}}
 print('motion',unit,'10.0..45.0, step 0.5, default 38.0')
(root/'decoded-motion-values.json').write_text(json.dumps(motion,indent=2)+'\n')

# Reduced, independent native commits: one edit per field on a committed baseline.
folder=root/'mame-reduced-commits'
reload_folder=root/'mame-reduced-reload'
if (reload_folder/'manifest.json').exists():
 reduced={}
 for directory in [folder,reload_folder,root/'mame-defaults']:
  m=json.loads((directory/'manifest.json').read_text())
  assert all(u['returncode']==0 and u['probe_ok'] for u in m['units'])
 for unit in manifest['plan']:
  samples=[(folder/unit/f'backup-{i:04}.bin').read_bytes() for i in range(1,9)]
  defaults=[49,35,35,30,30]
  for k,value in enumerate(defaults):
   assert read_time(folder/unit/'screen-0001.png',k)==value
   assert read_time(folder/unit/f'screen-{k+2:04}.png',k)==value+1
   offsets=[0xa+2*k+delta for delta in [0,0x100,0x200]]
   before,after=samples[k],samples[k+1]
   assert [i for i,(a,b) in enumerate(zip(before,after)) if a!=b]==offsets
   assert all(int.from_bytes(after[o:o+2],'little')==value+1 for o in offsets)
   assert read_time(reload_folder/unit/'screen-0001.png',k)==value+1
  assert samples[5]==samples[6], 'Uncommitted motion edit must not modify Backup RAM'
  assert read_motion(folder/unit/'screen-0007.png')==385
  offsets=[0x1a,0x11a,0x21a]
  assert [i for i,(a,b) in enumerate(zip(samples[6],samples[7])) if a!=b]==offsets
  assert all(int.from_bytes(samples[7][o:o+2],'little')==385 for o in offsets)
  assert read_motion(reload_folder/unit/'screen-0002.png')==385
  game=unit.split('-',1)[1]
  assert samples[-1]==(folder/unit/'nvram'/game/'backup1').read_bytes()
  files=list((folder/unit).glob('backup-*.bin'))+list((folder/unit).glob('screen-*.png'))+list((reload_folder/unit).glob('screen-*.png'))+list((reload_folder/unit).glob('backup-*.bin'))
  reduced[unit]={'native_commit':True,'fresh_process_reload':True,'time_values':[v+1 for v in defaults],'motion_tenths':385,'uncommitted_motion_preserves_backup':True,'files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
  print('reduced mapping and reload',unit,'OK')
 integrity={}
 for trial,expected in [('one-copy',50),('two-copies',80)]:
  run=root/f'mame-integrity-{trial}'
  if not (run/'manifest.json').exists():continue
  m=json.loads((run/'manifest.json').read_text())
  assert all(u['returncode']==0 and u['probe_ok'] for u in m['units'])
  integrity[trial]={}
  for unit in reduced:
   image_path=run/unit/'screen-0001.png';backup_path=run/unit/'backup-0001.bin'
   b=backup_path.read_bytes()
   assert read_time(image_path,0)==expected
   assert all(int.from_bytes(b[o:o+2],'little')==expected for o in [10,266,522])
   integrity[trial][unit]={'reloaded':expected,'all_copies_repaired':True,'files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [image_path,backup_path]}}
 result={'integrity_probe':integrity,'status':'numeric_fields_verified','sets':reduced,'time':{'encoding':'u16le_seconds','base_offsets':[10,12,14,16,18],'copy_stride':256,'copies':3,'minimum':5,'maximum':99,'step':1,'use_default':defaults},'motion':{'encoding':'u16le_tenths_of_degree','base_offset':26,'copy_stride':256,'copies':3,'minimum':100,'maximum':450,'step':5,'use_default':380},'country':{'observed_label':'Export','stable_after_calls':8,'encoding':'unresolved: native images contain 0 and 1 while displaying Export; no selectable region inferred'},'calibration':{'page':'Volume Setting','policy':'listed_only_excluded_from_acquisition_and_presets'},'pending':['native_integrity_algorithm','country_encoding','complete_initial_template','core_import_validation','core_option_review','automatic_policy','linked_gameplay']}
 import_root=root/'core-native-import'
 if (import_root/'summary.json').exists():
  summary=json.loads((import_root/'summary.json').read_text())
  assert len(summary)==1 and summary[0]['status']=='ok'
  native=import_root/'saves/powsledm-native-import-reload.nv'
  b=native.read_bytes();assert len(b)==16384
  for k,v in enumerate([50,36,36,31,31]):
   assert all(int.from_bytes(b[o:o+2],'little')==v for o in [10+2*k,266+2*k,522+2*k])
  assert all(int.from_bytes(b[o:o+2],'little')==385 for o in [26,282,538])
  files=list((import_root/'screenshots').glob('*.png'))+list((import_root/'saves').glob('*'))+[import_root/'summary.json']
  result['core_import']={'set':'powsledm','method':'RetroArch native NVRAM import; both screenshots visually reviewed; raw save words verified','time_values':[50,36,36,31,31],'motion_tenths':385,'files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'limits':'Slave/Relay core menu import remains unverified because of network startup'}
 (root/'operator-settings-observations.json').write_text(json.dumps(result,indent=2)+'\n')
