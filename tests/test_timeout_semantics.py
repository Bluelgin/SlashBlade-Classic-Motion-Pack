import json
from pathlib import Path
import tempfile
import unittest

from scripts.generate_motions import (
    VANILLA_SWING_FRAMES,
    generate,
    last_legacy_move,
    legacy_reset_frames,
    resolve_recovery,
    timeout_target,
)
from tools.vmd.codec import decode
from tools.vmd.legacy import pose

ROOT = Path(__file__).resolve().parents[1]


class TimeoutSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        legacy = json.loads((ROOT / 'data/legacy_motion_map.json').read_text())
        cls.combos = {entry['name']: entry for entry in legacy['entries']}
        cls.slots = json.loads((ROOT / 'data/bake_slots.json').read_text())['slots']
        cls.by_name = {slot['name']: slot for slot in cls.slots}

    def assert_key_pose(self, key, expected, msg):
        position, rotation = expected
        for actual, wanted in zip(key.position, position):
            self.assertAlmostEqual(actual, wanted, places=5, msg=f'{msg} position')
        # q and -q encode the same orientation.
        dot = abs(sum(a * b for a, b in zip(key.rotation, rotation)))
        self.assertGreater(dot, 1.0 - 1e-5, msg=f'{msg} rotation')

    def test_source_timed_slots_use_pinned_r32_reset_clocks(self):
        expected = {
            'A1': 31,
            'A2': 130,
            'A3 / Sakura right': 218,
            'C / Drive horizontal': 418,
            'A4': 546,
            'B / Circle': 763,
            'A4 EX': 855,
            'A5': 956,
            'Aerial A2 / Sakura right air': 1238,
            'Aerial A3 / Sakura left air': 1338,
            'Aerial B3': 1438,
            'Aerial B4': 1518,
            'Upper / Drive vertical / Wave Edge': 1630,
            'Cleave / Sakura left': 1836,
            'Judgement Cut': 1935,
            'Rapid Slash': 2018,
            'Rising Star': 2118,
            'Void Slash': 2212,
        }
        for name, frame in expected.items():
            slot = self.by_name[name]
            self.assertEqual(slot.get('recovery_mode'), 'legacy_reset', name)
            legacy_name, origin = last_legacy_move(slot)
            calculated = min(
                slot['end'],
                origin + legacy_reset_frames(self.combos[legacy_name]),
            )
            self.assertEqual(calculated, frame, name)
            self.assertEqual(slot['recovery_start'], frame, name)
            self.assertEqual(resolve_recovery(slot, self.combos), frame, name)

        # These modern windows are shorter than the old reset clocks. Keep them
        # explicit approximations instead of pretending a clamped timeout is exact.
        self.assertNotEqual(self.by_name['Aerial A1'].get('recovery_mode'), 'legacy_reset')
        self.assertNotEqual(self.by_name['Upper jump'].get('recovery_mode'), 'legacy_reset')

    def test_r32_timeout_targets_are_not_all_noutou(self):
        # r32 ItemSlashBlade.onUpdate resets scabbard moves and the
        # SlashDim/Iai/SIai family directly to None. Other mapped blade moves
        # enter Noutou and restart the vanilla swing.
        direct_none = {
            'A1',
            'A2',
            'A3 / Sakura right',
            'Judgement Cut',
            'Void Slash',
        }
        noutou = {
            'C / Drive horizontal',
            'A4',
            'B / Circle',
            'A4 EX',
            'A5',
            'Aerial A2 / Sakura right air',
            'Aerial A3 / Sakura left air',
            'Aerial B3',
            'Aerial B4',
            'Upper / Drive vertical / Wave Edge',
            'Cleave / Sakura left',
            'Rapid Slash',
            'Rising Star',
        }
        for name in direct_none:
            self.assertEqual(timeout_target(self.by_name[name], self.combos), 'none', name)
        for name in noutou:
            self.assertEqual(timeout_target(self.by_name[name], self.combos), 'noutou', name)

    def test_encoded_vmd_enters_the_same_timeout_state_as_r32(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            report = generate(output)
            motion = decode((output / 'assets/slashblade/combostate/motion.vmd').read_bytes())
            keys = {(key.bone, key.frame): key for key in motion.keys}
            reported = {entry['slot']: entry for entry in report}

            samples = {
                'A1': ('none', 31),
                'A3 / Sakura right': ('none', 218),
                'A4': ('noutou', 546),
                'Judgement Cut': ('none', 1935),
                'Rapid Slash': ('noutou', 2018),
                'Void Slash': ('none', 2212),
            }
            for slot_name, (target, frame) in samples.items():
                self.assertEqual(reported[slot_name]['timeout_target'], target)
                self.assertEqual(reported[slot_name]['recovery'], frame)
                for bone, sheath in (('hardpointA', False), ('hardpointB', True)):
                    expected = pose(
                        self.combos['None' if target == 'none' else 'Noutou'],
                        0,
                        sheath,
                    )
                    self.assert_key_pose(
                        keys[(bone, frame)],
                        expected,
                        f'{slot_name} {bone} frame={frame}',
                    )

            # A4's Noutou state is a fresh vanilla six-tick swing. The bake keeps
            # it for nine 30-Hz frames and then becomes neutral.
            neutral_frame = 546 + VANILLA_SWING_FRAMES
            for bone, sheath in (('hardpointA', False), ('hardpointB', True)):
                self.assert_key_pose(
                    keys[(bone, neutral_frame)],
                    pose(self.combos['None'], 0, sheath),
                    f'A4 {bone} frame={neutral_frame}',
                )


if __name__ == '__main__':
    unittest.main()
