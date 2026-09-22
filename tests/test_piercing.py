import json
from pathlib import Path
import tempfile
import unittest

from scripts.generate_motions import (
    PIERCING_ACTIVE_FRAME,
    PIERCING_MAX_FRAME,
    VANILLA_SWING_FRAMES,
    generate,
    legacy_reset_frames,
    noutou_state_frames,
)
from tools.vmd.codec import decode
from tools.vmd.legacy import pose

ROOT = Path(__file__).resolve().parents[1]


class PiercingClassicInterpretationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        legacy = json.loads((ROOT / 'data/legacy_motion_map.json').read_text())
        cls.combos = {entry['name']: entry for entry in legacy['entries']}
        cls.policy = json.loads((ROOT / 'data/piercing_classic_policy.json').read_text())

    def assert_key_pose(self, key, expected, msg):
        position, rotation = expected
        for actual, wanted in zip(key.position, position):
            self.assertAlmostEqual(actual, wanted, places=5, msg=f'{msg} position')
        dot = abs(sum(a * b for a, b in zip(key.rotation, rotation)))
        self.assertGreater(dot, 1.0 - 1e-5, msg=f'{msg} rotation')

    def test_policy_matches_pinned_modern_windows_and_r32_clock(self):
        blade_entries = json.loads((ROOT / 'data/resharped_blade_frame_map.json').read_text())['entries']
        modern = {
            row['id']: (row['start'], row['end'], row['resource'])
            for row in blade_entries
            if row['id'].startswith('slashblade:piercing')
        }
        for row in self.policy['target']['modern_windows']:
            self.assertIn(row['id'], modern)
            start, end, resource = modern[row['id']]
            self.assertEqual((start, end), (row['start'], row['end']))
            self.assertEqual(resource, self.policy['target']['blade_resource'])

        self.assertEqual(self.policy['adaptation'], 'CLASSIC_INTERPRETATION')
        self.assertEqual(self.policy['legacy_reference']['move'], 'Stinger')
        recovery = PIERCING_ACTIVE_FRAME + legacy_reset_frames(self.combos['Stinger'])
        self.assertEqual(recovery, 63)
        self.assertEqual(self.policy['legacy_reference']['recovery_frame'], recovery)
        self.assertEqual(noutou_state_frames(self.combos), 15)
        self.assertEqual(
            self.policy['legacy_reference']['neutral_frame'],
            recovery + noutou_state_frames(self.combos),
        )

    def test_generated_piercing_is_neutral_then_stinger_then_delayed_noutou(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            report = generate(output)
            motion = decode((output / 'assets/slashblade/combostate/piercing.vmd').read_bytes())
            keys = {(key.bone, key.frame): key for key in motion.keys}
            recovery = PIERCING_ACTIVE_FRAME + legacy_reset_frames(self.combos['Stinger'])
            neutral = recovery + noutou_state_frames(self.combos)

            for bone, sheath in (('hardpointA', False), ('hardpointB', True)):
                self.assert_key_pose(
                    keys[(bone, 1)],
                    pose(self.combos['None'], 0, sheath),
                    f'{bone} charge neutral',
                )
                self.assert_key_pose(
                    keys[(bone, PIERCING_ACTIVE_FRAME)],
                    pose(self.combos['Stinger'], 1, sheath),
                    f'{bone} Stinger start',
                )
                self.assert_key_pose(
                    keys[(bone, recovery - 1)],
                    pose(self.combos['Stinger'], 1, sheath),
                    f'{bone} Stinger hold',
                )
                self.assert_key_pose(
                    keys[(bone, recovery)],
                    pose(self.combos['Noutou'], 0, sheath),
                    f'{bone} Noutou recovery',
                )
                self.assert_key_pose(
                    keys[(bone, recovery + VANILLA_SWING_FRAMES)],
                    pose(self.combos['Noutou'], 1, sheath),
                    f'{bone} Noutou final swing pose',
                )
                self.assert_key_pose(
                    keys[(bone, neutral - 1)],
                    pose(self.combos['Noutou'], 1, sheath),
                    f'{bone} Noutou hold',
                )
                self.assert_key_pose(
                    keys[(bone, neutral)],
                    pose(self.combos['None'], 0, sheath),
                    f'{bone} neutral finish',
                )
                frames = {key.frame for key in motion.tracks()[bone]}
                self.assertEqual(frames, set(range(PIERCING_MAX_FRAME + 1)))

            reported = {entry['slot']: entry for entry in report}
            self.assertEqual(reported['Piercing dedicated atlas']['legacy'], 'Stinger')
            self.assertEqual(reported['Piercing dedicated atlas']['recovery'], recovery)
            self.assertEqual(reported['Piercing dedicated atlas']['timeout_target'], 'noutou')
            self.assertEqual(reported['Piercing dedicated atlas']['neutral'], neutral)

    def test_piercing_player_vmd_is_full_passthrough(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            generate(output)
            motion = decode((output / 'assets/slashblade/combostate/piercing_pl.vmd').read_bytes())
            tracks = motion.tracks()
            self.assertEqual(set(tracks), {'classic_root'})
            self.assertEqual(
                {key.frame for key in tracks['classic_root']},
                set(range(PIERCING_MAX_FRAME + 1)),
            )
            for key in tracks['classic_root']:
                self.assertEqual(key.position, (0.0, 0.0, 0.0))
                self.assertEqual(key.rotation, (0.0, 0.0, 0.0, 1.0))


if __name__ == '__main__':
    unittest.main()
