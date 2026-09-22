"""Validate runtime structure, generated effects, VMD data, rig and pinned frame windows."""
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
          'assets/slashblade/combostate/piercing.vmd','assets/slashblade/combostate/piercing_pl.vmd',
          'assets/slashblade/model/pa/player_motion.vmd','assets/slashblade/model/pa/alex.pmd',
          'assets/slashblade/model/util/slash.obj','assets/slashblade/model/util/slash.png',
          'assets/slashblade/model/util/drive.obj','assets/slashblade/model/util/ss.png'}


def _png_size(data, label):
    if not data.startswith(b'\x89PNG\r\n\x1a\n') or data[12:16] != b'IHDR':
        raise ValueError(f'Invalid PNG: {label}')
    return struct.unpack('>II', data[16:24])


def _validate_obj(data, label, minimum_faces):
    try:text=data.decode('ascii')
    except UnicodeDecodeError as e:raise ValueError(f'Non-ASCII generated OBJ: {label}') from e
    lines=[line.strip() for line in text.splitlines() if line.strip() and not line.startswith('#')]
    if 'g base' not in lines:raise ValueError(f'Missing base group: {label}')
    vertices=[line for line in lines if line.startswith('v ')]
    texcoords=[line for line in lines if line.startswith('vt ')]
    faces=[line for line in lines if line.startswith('f ')]
    if len(vertices)<8 or len(texcoords)<8 or len(faces)<minimum_faces:
        raise ValueError(f'Effect OBJ too small: {label}')
    if any(len(line.split()) not in (4,5) for line in faces):
        raise ValueError(f'Unsupported face arity: {label}')
    return len(vertices),len(faces)


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

    # These paths are hard-coded by Resharped renderers, so validating them in
    # the final ZIP proves the resource-pack override is structurally active.
    if _png_size(files['assets/slashblade/model/util/slash.png'],'slash.png')!=(128,32):
        raise ValueError('Unexpected classic trail texture size')
    if _png_size(files['assets/slashblade/model/util/ss.png'],'ss.png')!=(16,16):
        raise ValueError('Unexpected classic Drive texture size')
    _validate_obj(files['assets/slashblade/model/util/slash.obj'],'slash.obj',24)
    _validate_obj(files['assets/slashblade/model/util/drive.obj'],'drive.obj',12)

    motions={p:decode(b) for p,b in files.items() if p.endswith('.vmd')}
    for kind in ('player','blade'):
        rows=json.loads((ROOT/f'data/resharped_{kind}_frame_map.json').read_text())['entries']
        for r in rows:
            p='assets/'+r['resource'].replace(':','/')
            if p not in motions:
                raise ValueError(f'Missing overridden resource {p}')
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

    # Piercing has its own blade and player VMD contracts; both must be generated
    # rather than silently falling back to the modern upstream clips.
    piercing=motions['assets/slashblade/combostate/piercing.vmd'].tracks()
    for name in ('hardpointA','hardpointB'):
        if {k.frame for k in piercing[name]}!=set(range(91)):
            raise ValueError(f'Piercing {name} does not cover 0..90')
    piercing_player=motions['assets/slashblade/combostate/piercing_pl.vmd'].tracks()
    if {k.frame for k in piercing_player.get('classic_root',[])}!=set(range(91)):
        raise ValueError('Piercing player passthrough does not cover 0..90')

    # Validate the exact original, bone-only adapter, including the absence of
    # body-part names. This is not evidence of gameplay or body restoration.
    from scripts.generate_motions import passthrough_pmd
    if files['assets/slashblade/model/pa/alex.pmd']!=passthrough_pmd():raise ValueError('Unexpected player rig')
    return {p:m.summary() for p,m in motions.items()}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('path',nargs='?',type=Path,default=ROOT/'pack')
    result=validate(ap.parse_args().path)
    print('PASS: structure, classic effect adapters, PMD adapter, overridden frame slots and VMD records')
    for p,m in result.items():print(f'{p}: {m["key_count"]} keys, {len(m["bones"])} bones')
    print('Runtime verification pending')