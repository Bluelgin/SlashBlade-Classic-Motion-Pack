"""Deterministic, standard-library-only resource pack build."""
import hashlib
from pathlib import Path
import shutil
import struct
import sys
import zipfile
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.generate_motions import generate as generate_motions
from scripts.generate_effects import generate as generate_effects
from scripts.validate_pack import validate, EXPECTED
ROOT=Path(__file__).resolve().parents[1]

def icon():
    # Original geometric blade mark. No upstream texture or image dependencies.
    size=64;pixels=[]
    for y in range(size):
        row=bytearray()
        for x in range(size):
            color=(22,26,35,255)
            if abs(x+y-63)<3 and 12<x<52:color=(217,228,235,255)
            if abs(x-y+25)<2 and 10<x<27:color=(211,154,63,255)
            if abs(x+y-63)<3 and 5<x<=12:color=(157,50,55,255)
            row.extend(color)
        pixels.append(b'\0'+row)
    def chunk(n,b):return struct.pack('>I',len(b))+n+b+struct.pack('>I',zlib.crc32(n+b)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(pixels),9))+chunk(b'IEND',b'')

def prepare_pack(pack=None):
    """Reset the generated staging tree while preserving static pack metadata."""
    pack=Path(pack) if pack is not None else ROOT/'pack'
    pack.mkdir(parents=True,exist_ok=True)
    meta=pack/'pack.mcmeta'
    if not meta.is_file():
        raise FileNotFoundError(f'Missing static resource-pack metadata: {meta}')
    for child in pack.iterdir():
        if child.name=='pack.mcmeta':
            continue
        if child.is_dir():shutil.rmtree(child)
        else:child.unlink()
    return pack

def build():
    pack=prepare_pack()
    generate_motions(pack)
    generate_effects(pack)
    (pack/'pack.png').write_bytes(icon())
    for name in ('README.md','LICENSE','THIRD_PARTY_NOTICES.md'):shutil.copyfile(ROOT/name,pack/name)
    validate(pack)
    out=ROOT/'dist/SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip';out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(EXPECTED):
            info=zipfile.ZipInfo(name,(2020,2,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,(pack/name).read_bytes(),compresslevel=9)
    validate(out)
    digest=hashlib.sha256(out.read_bytes()).hexdigest()
    out.with_suffix('.zip.sha256').write_text(f'{digest}  {out.name}\n')
    print(f'{out}\nSHA256 {digest}\nRuntime verification pending')
    return out

if __name__=='__main__':build()
