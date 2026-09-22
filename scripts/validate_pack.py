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


def _validate_obj(data, label, minimum_faces, minimum_vertices=8):
    try:text=data.decode('ascii')
    except UnicodeDecodeError as e:raise ValueError(f'Non-ASCII generated OBJ: {label}') from e
    lines=[line.strip() for line in text.splitlines() if line.strip() and not line.startswith('#')]
    if 'g base' not in lines:raise ValueError(f'Missing base group: {label}')
    vertices=[line for line in lines if line.startswith('v ')]
    texcoords=[line for line in lines if line.startswith('vt ')]
    faces=[line for line in lines if line.startswith('f ')]
    if len(vertices)<minimum_vertices or len(texcoords)<minimum_vertices or len(faces)<minimum_faces:
        raise ValueError(f'Effect OBJ too small: {label}')
    if any(len(line.split()) not in (4,5) for line in faces):
        raise ValueError(f'Unsupported face arity: {label}')
    return len(vertices),len(faces)


def _rgba8_pixels(data, label):
    if _png_size(data,label)!=(1,1):raise ValueError(f'Unexpected suppression texture size: {label}')
    pos=8;idat=bytearray()
    while pos<len(data):
        size=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];payload=data[pos+8:pos+8+size]
        pos+=12+size
        if kind==b'IHDR':
            _,_,depth,color,_,_,_=struct.unpack('>IIBBBBB',payload)
            if depth!=8 or color!=6:raise ValueError(f'Expected RGBA8: {label}')
        elif kind==b'IDAT':idat.extend(payload)
        elif kind==b'IEND':break
    raw=__import__('zlib').decompress(bytes(idat))
    if raw!=b'\x00\x00\x00\x00\x00':raise ValueError(f'Slash suppression texture is not transparent: {label}')


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

    # slash.obj/png intentionally suppress Resharped's modern EntitySlashEffect
    # visual while leaving its Java entity/gameplay behavior untouched.
    _rgba8_pixels(files['assets/slashblade/model/util/slash.png'],'slash.png')
    slash_vertices,slash_faces=_validate_obj(files['assets/slashblade/model/util/slash.obj'],'slash.obj',1,4)
    if (slash_vertices,slash_faces)!=(4,1):raise ValueError('Unexpected slash suppression mesh')
    slash_text=files['assets/slashblade/model/util/slash.obj'].decode('ascii')
    coords=[]
    for line in slash_text.splitlines():
        if line.startswith('v '):coords.extend(float(v) for v in line.split()[1:4])
    if max(abs(v) for v in coords)>=0.00001:raise ValueError('Slash suppression mesh is visible-sized')

    if _png_size(files['assets/slashblade/model/util/ss.png'],'ss.png')!=(16,16):
        raise ValueError('Unexpected classic Drive texture size')
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

    piercing=motions['assets/slashblade/combostate/piercing.vmd'].tracks()
    for name in ('hardpointA','hardpointB'):
        if {k.frame for k in piercing[name]}!=set(range(91)):
            raise ValueError(f'Piercing {name} does not cover 0..90')
    piercing_player=motions['assets/slashblade/combostate/piercing_pl.vmd'].tracks()
    if {k.frame for k in piercing_player.get('classic_root',[])}!=set(range(91)):
        raise ValueError('Piercing player passthrough does not cover 0..90')

    from scripts.generate_motions import passthrough_pmd
    if files['assets/slashblade/model/pa/alex.pmd']!=passthrough_pmd():raise ValueError('Unexpected player rig')
    return {p:m.summary() for p,m in motions.items()}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('path',nargs='?',type=Path,default=ROOT/'pack')
    result=validate(ap.parse_args().path)
    print('PASS: structure, slash-light suppression, classic Drive adapter, PMD adapter, overridden frame slots and VMD records')
    for p,m in result.items():print(f'{p}: {m["key_count"]} keys, {len(m["bones"])} bones')
    print('Runtime verification pending')
