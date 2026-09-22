import json
from pathlib import Path
import struct
import sys
import unittest
import zlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.generate_effects import (
    classic_drive_obj, classic_drive_png, classic_trail_obj, classic_trail_png,
    generate, SLASH_OBJ, SLASH_PNG, DRIVE_OBJ, DRIVE_PNG,
)


def parse_obj(text):
    vertices=[];groups=[];faces=[]
    current=None
    for raw in text.splitlines():
        line=raw.strip()
        if line.startswith('v '):vertices.append(tuple(float(v) for v in line.split()[1:4]))
        elif line.startswith('g '):
            current=line.split(maxsplit=1)[1];groups.append(current)
        elif line.startswith('f '):faces.append((current,line.split()[1:]))
    return vertices,groups,faces


def decode_rgba_png(data):
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):raise AssertionError('not png')
    pos=8;idat=bytearray();width=height=None
    while pos<len(data):
        size=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];payload=data[pos+8:pos+8+size]
        pos+=12+size
        if kind==b'IHDR':width,height,depth,color,_,_,_=struct.unpack('>IIBBBBB',payload)
        elif kind==b'IDAT':idat.extend(payload)
        elif kind==b'IEND':break
    if depth!=8 or color!=6:raise AssertionError('expected rgba8')
    raw=zlib.decompress(bytes(idat));stride=width*4+1;pixels=[]
    for y in range(height):
        row=raw[y*stride:(y+1)*stride]
        if row[0]!=0:raise AssertionError('expected filter zero')
        pixels.append([tuple(row[1+x*4:1+(x+1)*4]) for x in range(width)])
    return width,height,pixels


class ClassicEffectTests(unittest.TestCase):
    def test_classic_trail_is_narrow_tapered_ribbon_not_modern_disc(self):
        vertices,groups,faces=parse_obj(classic_trail_obj())
        self.assertEqual(groups,['base'])
        self.assertEqual(len(faces),28)
        self.assertTrue(all(len(face)==4 for _,face in faces))
        radii=[(x*x+z*z)**0.5 for x,_,z in vertices]
        self.assertGreater(min(radii),45)
        self.assertLess(max(radii),85)
        self.assertLess(max(abs(y) for _,y,_ in vertices),1.0)
        widths=[]
        for i in range(0,len(vertices),2):
            a=vertices[i];b=vertices[i+1]
            widths.append(((a[0]-b[0])**2+(a[2]-b[2])**2)**0.5)
        self.assertLess(widths[0],4.0)
        self.assertGreater(max(widths),16.0)
        self.assertLess(widths[-1],4.0)

    def test_classic_trail_texture_has_bright_core_and_transparent_ends(self):
        w,h,p=decode_rgba_png(classic_trail_png())
        self.assertEqual((w,h),(128,32))
        self.assertEqual(p[h//2][0][3],0)
        self.assertEqual(p[h//2][-1][3],0)
        self.assertGreater(p[h//2][w//2][3],200)
        self.assertLess(p[0][w//2][3],20)

    def test_drive_bakes_r32_prism_into_modern_fixed_transform(self):
        vertices,groups,faces=parse_obj(classic_drive_obj())
        self.assertEqual(groups,['base'])
        self.assertEqual(len(vertices),14)
        self.assertEqual(len(faces),12)
        self.assertAlmostEqual(vertices[0][0],33.333333,5)
        self.assertAlmostEqual(vertices[0][1],66.666667,5)
        self.assertAlmostEqual(vertices[0][2],0.0,5)
        self.assertAlmostEqual(vertices[13][0],33.333333,5)
        self.assertAlmostEqual(vertices[13][1],-66.666667,5)
        self.assertEqual(decode_rgba_png(classic_drive_png())[:2],(16,16))

    def test_effect_contract_covers_all_fixed_renderer_families(self):
        data=json.loads((ROOT/'data/effect_resource_contract.json').read_text())
        rows={row['id']:row for row in data['contracts']}
        self.assertEqual(set(rows),{'entity_slash_effect','entity_drive','entity_judgement_cut'})
        self.assertEqual(rows['entity_slash_effect']['model'],'slashblade:model/util/slash.obj')
        self.assertIn('Void Slash',rows['entity_slash_effect']['coverage'])
        self.assertEqual(rows['entity_drive']['pack_action'],'BAKE_R32_PROCEDURAL_DRIVE_PRISM')
        jc=rows['entity_judgement_cut']
        self.assertEqual(jc['modern_model_git_blob'],jc['legacy_model_git_blob'])
        self.assertEqual(jc['modern_texture_git_blob'],jc['legacy_texture_git_blob'])
        self.assertEqual(jc['pack_action'],'LEAVE_INSTALLED_RESHARPED_ASSET_UNTOUCHED')

    def test_generator_writes_only_the_effect_overrides_we_intend(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            output=generate(Path(td))
            self.assertEqual(set(output),{SLASH_OBJ,SLASH_PNG,DRIVE_OBJ,DRIVE_PNG})
            for rel,payload in output.items():
                self.assertEqual((Path(td)/rel).read_bytes(),payload)
            # Judgement Cut is deliberately absent: Resharped already ships the
            # exact r32 slashdim model/texture blobs, so copying art is needless.
            self.assertFalse((Path(td)/'assets/slashblade/model/util/slashdim.obj').exists())


if __name__=='__main__':unittest.main()
