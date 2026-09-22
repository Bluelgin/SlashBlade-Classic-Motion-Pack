import dataclasses
import json
from pathlib import Path
import struct
import tempfile
import unittest
from tools.vmd.codec import Motion,Key,decode,remap,merge
from tools.vmd.legacy import pose,legacy_world,progress,dynamic
from tools.vmd.transforms import chain,from_pose,translation as T,scale as S,rotate as R
from scripts.generate_motions import generate,passthrough_pmd,legacy_reset_frames,last_legacy_move,resolve_recovery

ROOT=Path(__file__).resolve().parents[1]

class CodecTests(unittest.TestCase):
    def setUp(self):self.motion=Motion('sample',[Key('腕',0),Key('腕',10,(1.,2.,3.))])
    def test_roundtrip_and_interpolation(self):
        self.assertEqual(decode(self.motion.encode()).encode(),self.motion.encode())
        r=remap(self.motion,0,10,100,151)
        self.assertEqual([k.frame for k in r.keys],[100,151])
        self.assertEqual(r.keys[1].interpolation,self.motion.keys[1].interpolation)
        self.assertEqual(r.keys[1].position,self.motion.keys[1].position)
    def test_fail_closed(self):
        for data in (b'',self.motion.encode()[:53],self.motion.encode()[:70],b'X'+self.motion.encode()[1:]):
            with self.assertRaises(ValueError):decode(data)
        for bad in (dataclasses.replace(self.motion.keys[0],frame=-1),
                    dataclasses.replace(self.motion.keys[0],rotation=(0,0,0,0)),
                    dataclasses.replace(self.motion.keys[0],position=(float('nan'),0,0)),
                    dataclasses.replace(self.motion.keys[0],bone='a'*16),
                    dataclasses.replace(self.motion.keys[0],interpolation=bytes([255])*64)):
            with self.assertRaises(ValueError):Motion('test',[bad]).encode()
        with self.assertRaises(ValueError):merge([self.motion,self.motion])
        with self.assertRaises(ValueError):remap(self.motion,1,9,100,110)
        dense=Motion('dense',[Key('a',f) for f in range(5)])
        with self.assertRaises(ValueError):remap(dense,0,4,0,1)
    def test_nonbone_sections_preserved_but_not_silently_retimed(self):
        morph=struct.pack('<I',1)+b'morph'.ljust(15,b'\0')+struct.pack('<If',2,.5)+bytes(16)
        m=Motion('m',self.motion.keys,morph)
        self.assertEqual(decode(m.encode()).tail,morph)
        with self.assertRaises(ValueError):remap(m,0,10,1,41)
        with self.assertRaises(ValueError):decode(m.encode()[:-1])
    def test_exporter_interpolation_padding_is_preserved(self):
        raw=bytearray(self.motion.keys[0].interpolation);raw[31]=204;raw[63]=255
        m=Motion('padding',[dataclasses.replace(self.motion.keys[0],interpolation=bytes(raw))])
        self.assertEqual(decode(m.encode()).keys[0].interpolation,bytes(raw))

class RetargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.combos={x['name']:x for x in json.loads((ROOT/'data/legacy_motion_map.json').read_text())['entries']}
    def test_reconstruct_legacy_render_transform(self):
        # Independent inverse check: recompute the actual modern layer matrix
        # with the produced hardpoint pose and compare to legacy world space.
        for c in self.combos.values():
            for t in (0,.1,.25,.5,.75,1):
                for sheath in (True,False):
                    p,q=pose(c,t,sheath)
                    modern=chain(T(0,1.5,0),S(.125),R('z',180),S(-1,1,1),from_pose(p,q),S(-1,1,1),S(8))
                    expected=legacy_world(c,t,sheath)
                    for i in range(4):
                        for j in range(4):self.assertAlmostEqual(modern[i][j],expected[i][j],places=10)
    def test_a1_and_a2_are_saya_strikes(self):
        a=self.combos['Saya1'];b=self.combos['Saya2']
        self.assertAlmostEqual(progress(.5,'Saya1'),.84)
        self.assertEqual(pose(a,.5,True),pose(a,.5,False))
        self.assertEqual(pose(a,1),pose(b,0))
        self.assertEqual(pose(b,1),pose(self.combos['None'],0))
    def test_ground_chain_uses_coherent_s_rank_sequence(self):
        slots=json.loads((ROOT/'data/bake_slots.json').read_text())['slots']
        by_name={x['name']:x for x in slots}
        self.assertEqual(by_name['A1']['legacy'],'Saya1')
        self.assertEqual(by_name['A2']['legacy'],'Saya2')
        self.assertEqual(by_name['A3 / Sakura right']['legacy'],'SIai')
        self.assertEqual(by_name['A4']['legacy'],'SSlashEdge')
        self.assertEqual(by_name['A4 EX']['legacy'],'SSlashEdge')
        self.assertEqual(by_name['A4 EX']['second_legacy'],'SReturnEdge')
        self.assertEqual(by_name['A5']['legacy'],'SSlashBlade')

        # SIai is the old quick draw-and-return curve. Unlike Battou's one-way
        # ease, it reaches the far pose and comes back during one vanilla swing,
        # which fits Resharped A3's two timeline hits much better.
        self.assertAlmostEqual(progress(0,'SIai'),0)
        self.assertAlmostEqual(progress(5/12,'SIai'),1)
        self.assertAlmostEqual(progress(5/6,'SIai'),0)

    def test_ground_recovery_uses_classic_combo_reset_clocks(self):
        slots=json.loads((ROOT/'data/bake_slots.json').read_text())['slots']
        by_name={x['name']:x for x in slots}
        expected={
            'A1':31,
            'A2':130,
            'A3 / Sakura right':218,
            'A4':546,
            'A4 EX':855,
            'A5':956,
        }
        for name,frame in expected.items():
            slot=by_name[name]
            self.assertEqual(slot['recovery_mode'],'legacy_reset')
            legacy,origin=last_legacy_move(slot)
            calculated=min(slot['end'],origin+legacy_reset_frames(self.combos[legacy]))
            self.assertEqual(calculated,frame)
            self.assertEqual(slot['recovery_start'],frame)
            self.assertEqual(resolve_recovery(slot,self.combos),frame)

        # A4 EX contains two old moves in one modern slot. The timeout belongs
        # to the final SReturnEdge clip, not to the A4 EX state start.
        legacy,origin=last_legacy_move(by_name['A4 EX'])
        self.assertEqual((legacy,origin),('SReturnEdge',817))

    def test_a3_siai_recovery_starts_at_classic_timeout_boundary(self):
        slots=json.loads((ROOT/'data/bake_slots.json').read_text())['slots']
        a3=next(x for x in slots if x['name']=='A3 / Sakura right')
        siai=self.combos['SIai']
        # comboResetTicks is a state-reset/timeout window, not the duration of
        # the visible swing. At 30 VMD frames / 20 game ticks, r32 SIai's
        # 12-tick reset lands 18 frames after modern slot start: 200 -> 218.
        expected=a3['start']+round(siai['reset_ticks']*30/20)
        self.assertEqual(expected,218)
        self.assertEqual(resolve_recovery(a3,self.combos),expected)

        modern=json.loads((ROOT/'data/resharped_blade_frame_map.json').read_text())['entries']
        by_id={x['id']:x for x in modern}
        # This same frame is a real modern state boundary for both consumers of
        # this shared atlas region: Combo A3 and Sakura End Right.
        self.assertEqual(by_id['slashblade:combo_a3']['end'],expected)
        self.assertEqual(by_id['slashblade:combo_a3_end']['start'],expected)
        self.assertEqual(by_id['slashblade:sakura_end_right']['end'],expected)
        self.assertEqual(by_id['slashblade:sakura_end_finish']['start'],expected)
    def test_all_build_frames_and_determinism(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);report=generate(p)
            files={str(x.relative_to(p)):x.read_bytes() for x in p.rglob('*') if x.is_file()}
            self.assertEqual({x['slot']:x['recovery'] for x in report if x['slot'] in {'A1','A2','A3 / Sakura right','A4','A4 EX','A5'}},
                             {'A1':31,'A2':130,'A3 / Sakura right':218,'A4':546,'A4 EX':855,'A5':956})
            generate(p)
            for name,b in files.items():self.assertEqual(b,(p/name).read_bytes())
            m=decode(files['assets/slashblade/combostate/motion.vmd'])
            tracks=m.tracks()
            for bone in ('hardpointA','hardpointB'):
                self.assertEqual([k.frame for k in tracks[bone]],list(range(2300)))
            for f in range(1,11):
                a=tracks['hardpointA'][f];b=tracks['hardpointB'][f]
                self.assertEqual(a.position,b.position);self.assertEqual(a.rotation,b.rotation)
    def test_player_adapter_is_not_a_fake_body_clip(self):
        b=passthrough_pmd()
        self.assertEqual(b[:3],b'Pmd')
        self.assertEqual(struct.unpack_from('<IIIH',b,283),(0,0,0,1))
        self.assertEqual(b[297:317].split(b'\0')[0],b'classic_root')
        for bone in (b'body',b'right arm',b'left arm',b'right leg',b'left leg'):
            self.assertNotEqual(b[297:317].split(b'\0')[0],bone)

if __name__=='__main__':unittest.main()
