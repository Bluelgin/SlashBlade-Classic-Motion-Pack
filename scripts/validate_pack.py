"""Validate runtime structure, VMD data, rig and all pinned frame windows."""
import argparse
import json
from pathlib import Path
import struct
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.vmd.codec import decode
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'pack.mcmeta','pack.png','README.md','LICENSE','THIRD_PARTY_NOTICES.md',
          'assets/slashblade/combostate/motion.vmd',
          'assets/slashblade/model/pa/player_motion.vmd','assets/slashblade/model/pa/alex.pmd'}

def validate(path):
    if path.is_file():
        with zipfile.ZipFile(path) as z:
            names=z.namelist()
            if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP entries')
            if z.testzip():raise ValueError('ZIP CRC failure')
            files={n:z.read(n) for n in names if not n.endswith('/')}
    else:files={p.relative_to(path).as_posix():p.read_bytes() for p in path.rglob('*') if p.is_file()}
    if set(files)!=EXPECTED:raise ValueError(f'Unexpected/missing runtime files: {set(files)^EXPECTED}')
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=15:raise ValueError('Wrong pack_format')
    icon=files['pack.png']
    if not icon.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Invalid icon')
    motions={p:decode(b) for p,b in files.items() if p.endswith('.vmd')}
    for kind in ('player','blade'):
        rows=json.loads((ROOT/f'data/resharped_{kind}_frame_map.json').read_text())['entries']
        for r in rows:
            p='assets/'+r['resource'].replace(':','/')
            if p not in motions:
                if r['resource'] not in ('slashblade:combostate/piercing.vmd','slashblade:combostate/piercing_pl.vmd'):
                    raise ValueError(f'Missing overridden resource {p}')
                continue  # Unmodified upstream resource, explicitly documented
            tracks=motions[p].tracks()
            required=('classic_root',) if kind=='player' else ('hardpointA','hardpointB')
            for bone in required:
                frames={k.frame for k in tracks.get(bone,[])}
                if not set(range(r['start'],r['end']+1))<=frames:
                    raise ValueError(f'Missing keys: {r["combo"]} {bone}')
    blade=motions['assets/slashblade/combostate/motion.vmd'].tracks()
    for name in ('hardpointA','hardpointB'):
        a1=[k for k in blade[name] if 1<=k.frame<=10]
        if len({k.position+k.rotation for k in a1})<5:raise ValueError('A1 is static')
    # Validate the exact original, bone-only adapter, including the absence of
    # body-part names. This is not evidence of gameplay or body restoration.
    from scripts.generate_motions import passthrough_pmd
    if files['assets/slashblade/model/pa/alex.pmd']!=passthrough_pmd():raise ValueError('Unexpected player rig')
    return {p:m.summary() for p,m in motions.items()}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('path',nargs='?',type=Path,default=ROOT/'pack')
    result=validate(ap.parse_args().path)
    print('PASS: structure, PMD adapter, all overridden frame slots and VMD records')
    for p,m in result.items():print(f'{p}: {m["key_count"]} keys, {len(m["bones"])} bones')
    print('Runtime verification pending')
