#!/usr/bin/env python3
"""Generate the complete linked RetroArch recipe from the finished Phase 1 YAML."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ['powsledm', 'powsledr', 'powsled']
OUT = ROOT/'scripts/libretro_nvram_samples.power-sled-linked.toml'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
parser.add_argument('--ride-campaign', type=Path, help='Generate the complete four-color extension campaign')
parser.add_argument('--phase1-run', type=Path, help='Validated target-core menu inventory run')
args = parser.parse_args()
if args.ride_campaign:
    if not args.phase1_run:
        parser.error('--ride-campaign requires --phase1-run')
    phase1 = args.phase1_run.resolve()
    review = json.loads((phase1.parent/'phase1-review.json').read_text())
    if review['status'] != 'four_color_inventory_validated' or Path(review['run']) != phase1:
        raise SystemExit('Four-color Phase 1 inventory is not validated')
    inventories = []
    for game in GAMES:
        path = ROOT/f'data/diagnostic-menus/{game}.yaml'
        spec = json.JSONDecoder().raw_decode(path.read_text().split('ride_color_extension:',1)[1].lstrip())[0]
        if spec['status'] != 'service_menu_documented' or len(spec['values']) != 4:
            raise SystemExit(f'Incomplete four-color inventory: {game}')
        inventories.append({'path':str(path.relative_to(ROOT)), 'scope':'ride_color_extension',
            'menu_sha256':hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()})
    samples = [{'suffix':'menu-baseline','setting':'ride_id','offset':8,'width':1,
        'expected':[0,0,1], 'screenshot':'initial','reload_only':True,'reuse':str(phase1)}]
    prior = 'menu-baseline'
    for value,color in enumerate(['silver','red','black','yellow']):
        steps = []
        for index,game in enumerate(GAMES):
            calls = (3 if index == 2 else 4) if value == 0 else 1
            steps.append({'sets':[game], 'sequence':['@enter_ride','SCREENSHOT(reloaded)',
                'L3*2',f'A*{calls}','SCREENSHOT(selected)','L3*2','A','WAIT(1.0)']})
        steps.append({'sets':GAMES,'sequence':['CLOSE']})
        name = 'commit-'+color
        samples.append({'suffix':name,'setting':'ride_id','offset':8,'width':1,
            'expected':[value]*3,'screenshot':'selected','before_screenshot':'reloaded',
            'baseline':prior,'steps':steps})
        prior = 'reload-'+color
        samples.append({'suffix':prior,'setting':'ride_id','offset':8,'width':1,
            'expected':[value]*3,'screenshot':'selected','baseline':name,'reload_only':True,
            'sequence':['@enter_ride','SCREENSHOT(selected)','CLOSE']})
    # JSON literals are TOML-compatible for these strings, numbers and arrays.
    text = 'schema_version = 1\nride_reference_root = '+json.dumps(str(phase1))+'\n'
    for source in inventories:
        text += '\n[[inventory]]\n'+''.join(k+' = '+json.dumps(v)+'\n' for k,v in source.items())
    text += '\n[macros]\nenter_ride = '+json.dumps(['R3','WAIT(2.0)','L3*6','A','WAIT(1.0)','L3*2','A','WAIT(1.0)'])+'\n'
    for sample in samples:
        text += '\n[[samples]]\n'
        for key,val in sample.items():
            if key=='steps': continue
            text += key+' = '+(str(val).lower() if isinstance(val,bool) else json.dumps(val))+'\n'
        for step in sample.get('steps',[]):
            text += '\n[[samples.steps]]\n'+''.join(k+' = '+json.dumps(v)+'\n' for k,v in step.items())
    if args.check:
        if args.ride_campaign.read_text() != text: raise SystemExit('Four-color recipe differs from inventory')
    else:
        args.ride_campaign.write_text(text)
    print('Four-color extension: one persistent recipe, four commits and four fresh reloads for all three sets')
    raise SystemExit(0)

inventories = []
menus = []
for game in GAMES:
    path = ROOT/f'data/diagnostic-menus/{game}.yaml'
    text = path.read_text()
    if 'status: service_menu_documented' not in text:
        raise SystemExit(f'Incomplete Phase 1: {game}')
    menu = json.JSONDecoder().raw_decode(text.split('menus:', 1)[1].lstrip())[0]
    menus.append(menu['game_assignments']['options'])
    inventories.append({'path': str(path.relative_to(ROOT)),
        'menu_sha256': hashlib.sha256(json.dumps(menu, sort_keys=True).encode()).hexdigest()})
assert all([o['key'] for o in m] == ['country', 'ride_id', 'checkpoint_0', 'checkpoint_1',
    'checkpoint_2', 'checkpoint_3', 'checkpoint_4', 'motion_angle'] for m in menus)
macros = {
 'enter_assignments': ['R3','WAIT(2.0)','L3*6','A','WAIT(1.0)'],
 'enter_time': ['@enter_assignments','L3*3','A','WAIT(1.0)'],
 'enter_motion': ['R3','WAIT(2.0)','L3*6','A','WAIT(1.0)','L3*4','A','WAIT(1.0)'],
 'enter_country': ['@enter_assignments','L3','A','WAIT(1.0)'],
 'enter_ride': ['@enter_assignments','L3*2','A','WAIT(1.0)'],
}
samples = []
def add(name, setting, offset, sequence=None, baseline=None, **kwargs):
    sample = {'suffix': name, 'setting': setting, 'offset': offset,
              'screenshot': 'selected', **kwargs}
    if sequence is not None: sample['sequence'] = sequence
    if baseline: sample['baseline'] = baseline
    samples.append(sample)
    return name
old = 'build-libretro-gpu/validation/power-sled-phase2-20261008/'
add('motion-native-default','motion',26,
 ['@enter_motion','SCREENSHOT(motion-before-default)','L3*4','A','SCREENSHOT(motion-default)',
  'L3*2','A','WAIT(1.0)','SCREENSHOT(after-native-commit)','CLOSE'],
 expected=[380]*3, screenshot='motion-default', reuse=old+'motion-native-default')
add('motion-plus-step','motion',26,
 ['@enter_motion','SCREENSHOT(motion-baseline)','L3*2','A','SCREENSHOT(motion-plus-step)',
  'L3*4','A','WAIT(1.0)','SCREENSHOT(after-native-commit)','CLOSE'],
 baseline='motion-native-default', expected=[385]*3, screenshot='motion-plus-step',
 before_screenshot='motion-baseline', reuse=old+'motion-plus-step')
add('motion-reload','motion',26,
 ['@enter_motion','SCREENSHOT(motion-reloaded)','CLOSE'],
 baseline='motion-plus-step', expected=[385]*3, screenshot='motion-reloaded',
 reload_only=True, reuse=old+'motion-reload')
# Every field has its own committed branch; other operator fields are preserved.
default_baseline = 'motion-native-default'
for index in range(5):
    options = [m[index+2] for m in menus]
    assert all(o['range'] == options[0]['range'] and o['native_default'] == options[0]['native_default'] for o in options)
    spec = options[0]
    low, high, step = [spec['range'][k] for k in ('minimum','maximum','step')]
    default = spec['native_default']
    previous, prior = default_baseline, None
    setting = f'checkpoint_{index}'
    for suffix, value in [('default',default),('step',default+step),('minimum',low),('maximum',high)]:
        seq = ['@enter_time']
        if prior is not None: seq += ['SCREENSHOT(reloaded)']
        seq += [f'L3*{index+1}','A','WAIT(0.6)']
        if prior is None:
            seq += ['L3*4','A','L3*2']  # Use Default, then Set & Exit.
        else:
            count = abs(value-prior)//step
            if value > prior:
                seq += ['L3*2',f'A*{count}','L3*4']
            else:
                seq += ['L3*3',f'A*{count}','L3*3']
        seq += ['A','WAIT(0.6)','SCREENSHOT(selected)','CLOSE']
        name = f'{setting.replace("_","-")}-{suffix}'
        add(name,setting,10+2*index,seq,previous,expected=[value]*3,
            **({'before_screenshot':'reloaded'} if prior is not None else {}))
        if prior is None: default_baseline = name
        previous,prior = name,value
    add(f'checkpoint-{index}-reload',setting,10+2*index,
        ['@enter_time','SCREENSHOT(selected)','CLOSE'],previous,expected=[prior]*3,reload_only=True)
# Motion representatives include the 255 -> 260 carry in the u16 stored word.
spec = menus[0][-1]
assert all(m[-1]['range']==spec['range'] for m in menus)
low = round(spec['range']['minimum']*10)
high = round(spec['range']['maximum']*10)
step = round(spec['range']['step']*10)
prior, previous = 380, 'motion-native-default'
for label,value in [('minimum',low),('byte-before',255),('byte-after',260),('maximum',high)]:
    seq = ['@enter_motion','SCREENSHOT(reloaded)']
    if value > prior: seq += ['L3*2',f'A*{(value-prior)//step}','SCREENSHOT(selected)','L3*4']
    else: seq += ['L3*3',f'A*{(prior-value)//step}','SCREENSHOT(selected)','L3*3']
    seq += ['A','WAIT(0.6)','SCREENSHOT(committed)','CLOSE']
    previous = add('motion-'+label,'motion',26,seq,previous,
                   expected=[value]*3,before_screenshot='reloaded')
    prior = value
add('motion-limits-reload','motion',26,['@enter_motion','SCREENSHOT(selected)','CLOSE'],
    previous,expected=[prior]*3,reload_only=True)
# Country is visibly Export throughout. Acquire stored states without region names.
previous = default_baseline
for n in range(3):
    seq = ['@enter_country']
    if n: seq += ['SCREENSHOT(reloaded)']
    seq += ['L3*2','A','SCREENSHOT(selected)','L3*2','A','WAIT(0.6)','CLOSE']
    previous = add('country-'+['initial','alternate','cycle-close'][n],'country',9,seq,previous,
        width=1,allowed=[0,1],**({'toggle':True,'before_screenshot':'reloaded'} if n else {}))
add('country-reload','country',9,['@enter_country','SCREENSHOT(selected)','CLOSE'],
    previous,width=1,allowed=[0,1],reload_only=True)
# Initialize all native Ride fields with their first reachable choice.
# With Country 0 and uninitialized Ride 255, Main's first call is Red.
# Normalize Main through the documented three-color cycle, commit it first,
# then enter Slave with Main held at Silver. Never cycle dependent peers together.
initialize_steps = [
 {'sets':['powsledm'],'sequence':['@enter_ride','SCREENSHOT(ride-uninitialized)',
    'L3*2','A','SCREENSHOT(initial-red)','A','SCREENSHOT(initial-black)','A',
    'SCREENSHOT(selected)','L3*2','A','WAIT(1.0)']},
 {'sets':['powsledr'],'sequence':['@enter_ride','SCREENSHOT(ride-uninitialized)',
    'L3*2','A','SCREENSHOT(selected)','L3*2','A','WAIT(1.0)']},
 {'sets':['powsled'],'sequence':['@enter_ride','SCREENSHOT(selected)']},
 {'sets':GAMES,'sequence':['CLOSE']}]
previous = add('ride-main-initialize','ride_id',8,baseline=previous,
               width=1,expected=[0,0,255],steps=initialize_steps,setup_only=True)
# Reload the committed Main before setting the dependent Slave color.
slave_initialize = [
 {'sets':GAMES,'sequence':['@enter_ride','SCREENSHOT(reloaded)']},
 {'sets':['powsled'],'sequence':['L3*2','A','SCREENSHOT(initial-red)','A',
    'SCREENSHOT(initial-black)','A','SCREENSHOT(selected)','L3*2','A','WAIT(1.0)']},
 {'sets':['powsledm','powsledr'],'sequence':['SCREENSHOT(selected)']},
 {'sets':GAMES,'sequence':['CLOSE']}]
previous = add('ride-initialize','ride_id',8,baseline=previous,
               width=1,expected=[0,0,0],steps=slave_initialize,
               before_screenshot='reloaded',bootstrap_reload=True)
# The reference fixes BOTH Main and Slave colors. A committed all-Silver
# topology stays Silver on both programs. Acquire each joint initialization
# independently from the unassigned target-core baseline, then its full cycle.
# This records the observed context without attributing the bound to Main alone.
ride_unassigned = 'country-cycle-close'
def ride_stage(name, baseline, value, calls, labels=None, bootstrap=False, reload=False, relay_raw=0):
    seq = ['@enter_ride','SCREENSHOT(reloaded)']
    if not reload:
        seq += ['L3*2']
        for index in range(calls):
            seq += ['A']
            if labels: seq += [f'SCREENSHOT({labels[index]})']
        seq += ['SCREENSHOT(selected)','L3*2','A','WAIT(1.0)']
    else:
        seq += ['SCREENSHOT(selected)']
    seq += ['CLOSE']
    return add(name,'ride_id',8,seq,baseline,width=1,expected=[value,"observed" if relay_raw is None else relay_raw,value],
        before_screenshot='reloaded',**({'allowed':[0,1,2]} if relay_raw is None else {}),
        **({'bootstrap_reload':True} if bootstrap else {}),
        **({'reload_only':True} if reload else {}))
silver = ride_stage('ride-silver-cycle', previous, 0, 1, ['cycle-silver'])
ride_stage('ride-silver-reload', silver, 0, 0, reload=True)
red = ride_stage('ride-red-initialize', ride_unassigned, 1, 1, ['initial-red'], bootstrap=True)
def fixed_peer_cycle(name, baseline, value, main_cycle, slave_cycle, relay_cycle, relay_raw):
    steps = [{'sets':GAMES,'sequence':['@enter_ride','SCREENSHOT(reloaded)']}]
    # Document each program independently while its peers hold their color.
    for game, colors in [('powsled',slave_cycle),('powsledm',main_cycle),('powsledr',relay_cycle)]:
        seq = ['L3*2'] if colors else []
        if colors and game!='powsledr': seq += [f'RIDE_CYCLE({value})']
        else:
            for color in colors: seq += ['A',f'SCREENSHOT(cycle-{color})']
        seq += ['SCREENSHOT(selected)']
        if colors: seq += ['L3*2','A','WAIT(1.0)']
        steps.append({'sets':[game], 'sequence':seq})
    steps.append({'sets':GAMES,'sequence':['CLOSE']})
    return add(name,'ride_id',8,baseline=baseline,width=1,expected=[value,"observed" if relay_raw is None else relay_raw,value],allowed=[0,1,2],
               before_screenshot='reloaded',steps=steps)
red_close = fixed_peer_cycle('ride-red-cycle', red, 1,
                            ['black','silver','red'], ['silver','red'], ['red'], None)
red_reload = ride_stage('ride-red-reload', red_close, 1, 0, reload=True, relay_raw=None)
relay_close = fixed_peer_cycle('ride-red-relay-repeat', red_reload, 1, [], [], ['silver'], None)
ride_stage('ride-red-relay-reload', relay_close, 1, 0, reload=True, relay_raw=None)
# Bootstrap Slave Black from the already proven Main-Silver/Slave-unassigned
# core context (the initializer captured all three colors there). Then restart
# the ring and commit Main Black while the initialized Slave stays fixed.
slave_black_steps = [
 {'sets':GAMES,'sequence':['@enter_ride','SCREENSHOT(reloaded)']},
 {'sets':['powsled'],'sequence':['L3*2','A','SCREENSHOT(initial-red)',
    'A','SCREENSHOT(initial-black)','SCREENSHOT(selected)','L3*2','A','WAIT(1.0)']},
 {'sets':['powsledm','powsledr'],'sequence':['SCREENSHOT(selected)']},
 {'sets':GAMES,'sequence':['CLOSE']}]
slave_black = add('ride-black-slave-initialize','ride_id',8,
    baseline='ride-main-initialize',width=1,expected=[0,0,2],steps=slave_black_steps,
    before_screenshot='reloaded',bootstrap_reload=True,setup_only=True)
main_black_steps = [
 {'sets':GAMES,'sequence':['@enter_ride','SCREENSHOT(reloaded)']},
 {'sets':['powsledm'],'sequence':['L3*2','A','SCREENSHOT(initial-red)',
    'A','SCREENSHOT(initial-black)','SCREENSHOT(selected)','L3*2','A','WAIT(1.0)']},
 {'sets':['powsledr','powsled'],'sequence':['SCREENSHOT(selected)']},
 {'sets':GAMES,'sequence':['CLOSE']}]
black = add('ride-black-initialize','ride_id',8,baseline=slave_black,width=1,
    expected=[2,0,2],steps=main_black_steps,before_screenshot='reloaded')
black_reload = ride_stage('ride-black-reload', black, 2, 0, reload=True)
# Further ID attribution/conditional-topology investigation is deferred by
# the user's instruction; mapping colors and fresh reload do not require it.
lines = ['# Generated from the completed Phase 1 inventory; do not hand-edit sample subsets.',
 '# Regenerate: python3 scripts/generate-power-sled-recipe.py',
 '# Target acquisition: SM2-Emu Libretro in RetroArch exclusively; no calibration.',
 'schema_version = 1','']
def emit(obj):
    for key,value in obj.items():
        lines.append(f'{key} = {json.dumps(value,ensure_ascii=False)}'.replace(': true',': true'))
for inv in inventories:
    lines += ['[[inventory]]']; emit(inv); lines.append('')
lines += ['[macros]']; emit(macros); lines.append('')
for sample in samples:
    lines += ['[[samples]]']; emit({k:v for k,v in sample.items() if k!='steps'})
    for step in sample.get('steps',[]):
        lines += ['[[samples.steps]]']; emit(step)
    lines.append('')
text = '\n'.join(lines)
if args.check:
    if OUT.read_text()!=text: raise SystemExit('Complete recipe is stale; regenerate from Phase 1')
else: OUT.write_text(text)
print(f'Power Sled: {len(samples)} planned stages; 3 programs; calibration excluded')
