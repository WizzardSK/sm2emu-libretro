#!/usr/bin/env python3
"""Run/resume the complete GTX recipe with per-stage native and reload gates.

Reuses libretro_nvram_samples for process/configuration/input/save acquisition;
this wrapper adds a persistent validated manifest and recipe-declared reloads.
"""
from dataclasses import asdict, replace
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tomllib
from PIL import Image, ImageChops
import libretro_nvram_samples as samples
from validate_nvram_batch2 import crc16, swapped_words

ROOT = Path(__file__).resolve().parent.parent
RECIPE = ROOT / 'scripts/libretro_nvram_samples.daytonagtx.toml'
FIELDS = {
    'link_id': (11, [1, 2, 0]), 'car_number': (12, list(range(8))),
    'cabinet': (26, [1, 2, 0]), 'country': (27, [1, 2, 0]),
    'difficulty': (32, [1, 2, 3, 0]), 'advertise_sound': (25, [0, 1]),
    'game_mode': (28, [0, 1, 2]), 'rival_arrow': (29, [0, 1]),
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate(path, field=None, step=0):
    data=path.read_bytes(); assert len(data)==16576 and data[:8]==b'SM2SRAM\0'
    assert data[24:56].split(b'\0',1)[0]==b'daytonagtx'
    assert int.from_bytes(data[20:24],'little')==crc16(data[64:])
    backup=data[64:64+16384]; eeprom=data[-128:]
    assert backup[:128]==backup[128:256], 'Native mirrored settings differ'
    assert int.from_bytes(backup[8:10],'little')==crc16(backup[10:128]), 'Native bank checksum differs'
    assert eeprom==swapped_words(backup[:128]), 'EEPROM/native settings differ'
    for key,(offset,values) in FIELDS.items():
        assert backup[offset]==values[step if key==field else 0], (key, backup[offset], field, step)
    return backup

def main():
    args=samples.parse_args(); settings, stages=samples.load_campaign(args)
    samples.validate_paths(settings)
    if args.dry_run:
        samples.print_dry_run(settings, stages); return
    if args.sample or args.resume_from or args.interactive:
        raise RuntimeError('Run the whole recipe; validated stages resume from the manifest')
    raw=tomllib.loads(RECIPE.read_text()); entries={e['suffix']:e for e in raw['samples']}
    root=settings.output_dir; root.mkdir(parents=True,exist_ok=True); (root/'saves').mkdir(exist_ok=True)
    manifest_path=root/'campaign.json'
    pin={'core_sha256':sha(settings.core),'recipe_sha256':sha(RECIPE)}
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {**pin,'plan':raw['samples'],'validated':{}}
    assert all(manifest[k]==v for k,v in pin.items()), 'Core/recipe changed; preserve evidence and use a new output'
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('gtx_linked_runner',ROOT/'scripts/test-retroarch-netpacket.py')
    linked=importlib.util.module_from_spec(spec);sys.modules[spec.name]=linked;spec.loader.exec_module(linked)
    original_config=samples.write_isolated_config;command_port=None
    def config(*args):
        nonlocal command_port
        command_port=args[3]; result=original_config(*args)
        with (args[1]/'nvram-samples-overrides.cfg').open('a') as out:
            out.write('auto_overrides_enable = "false"\nauto_remaps_enable = "false"\nsavestate_auto_save = "false"\nsavestate_auto_load = "false"\n')
        return result
    samples.write_isolated_config=config
    samples.activate_process=lambda process: None
    def close(process, _):
        assert not linked.close_instance(process,command_port) and process.returncode==0, 'Owned RetroArch shutdown failed'
    samples.close_retroarch=close
    for index,stage in enumerate(stages,1):
        name=stage.suffix; entry=entries[name]; saved=manifest['validated'].get(name)
        if saved and all(Path(p).exists() and sha(p)==h for p,h in saved['files'].items()):
            print(f'[{index}/{len(stages)}] {name}: validated, reused',flush=True);continue
        tries=root/'attempts';tries.mkdir(exist_ok=True);attempt=1
        while (tries/f'{name}-{attempt:02d}').exists():attempt+=1
        output=tries/f'{name}-{attempt:02d}';output.mkdir();(output/'saves').mkdir();(output/'logs').mkdir()
        baseline=entry.get('reload_of','base') if name!='base' else None
        config=replace(settings,output_dir=output,baseline_sample=None,standard_srm=root/'saves'/f'daytonagtx-{baseline}.srm' if baseline else None)
        print(f'[{index}/{len(stages)}] {name}: acquire',flush=True)
        result=samples.run_sample(config,stage,False,False)
        (output/'result.json').write_text(json.dumps(asdict(result),indent=2)+'\n')
        assert result.status=='ok', result.note
        srm=output/'saves'/f'daytonagtx-{name}.srm';field=entry.get('field');step=entry.get('step',0)
        actual=Path(result.screenshots[0])
        reference=ROOT/'build-libretro-gpu/validation/daytonagtx-service-20261017/menu-run/screenshots/game-system-default.png'
        with Image.open(reference) as a,Image.open(actual) as b:
            assert ImageChops.difference(a.convert('L').crop((400,40,620,68)).point(lambda p: 255 if p else 0),b.convert('L').crop((400,40,620,68)).point(lambda p: 255 if p else 0)).getbbox() is None, 'Service Menu not reached; no sample qualified'
        validate(srm,field,step)
        if field:
            position=list(FIELDS).index(field); expected=ROOT/f'build-libretro-gpu/validation/daytonagtx-service-20261017/menu-run/screenshots/{field.replace("_","-")}-{step:02d}.png'
            actual=Path(result.screenshots[0])
            with Image.open(expected) as a,Image.open(actual) as b:
                assert a.size==b.size==(1024,768), (a.size,b.size)
                region=(590,80+position*32,900,100+position*32)
                assert ImageChops.difference(a.convert('L').crop(region).point(lambda p: 255 if p else 0),b.convert('L').crop(region).point(lambda p: 255 if p else 0)).getbbox() is None, 'Visible native value differs from independent Phase 1 screen'
        if entry.get('reload_of'):
            source=root/'saves'/f'daytonagtx-{entry["reload_of"]}.srm'
            assert srm.read_bytes()[64:320]==source.read_bytes()[64:320], 'Native settings changed after fresh reload'
        shutil.copy2(srm,root/'saves'/srm.name)
        files={str(p):sha(p) for p in [srm,*map(Path,result.screenshots),Path(result.log)]}
        manifest['validated'][name]={'files':files,'field':field,'step':step,'reload_of':entry.get('reload_of'),'native_integrity':True,'visible_value':True,'result':str(output/'result.json')}
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');print('  validated',flush=True)
    print(f'Complete: {len(manifest["validated"])} validated stages',flush=True)

if __name__=='__main__':
    main()
