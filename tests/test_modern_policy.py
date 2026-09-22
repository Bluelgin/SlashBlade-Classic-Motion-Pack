import json
from pathlib import Path
import tempfile
import unittest

from scripts.generate_motions import generate, timeout_target
from tools.slot_topology import (
    by_id,
    external_consumers,
    family_window,
    overlap_frames,
)
from tools.vmd.codec import decode
from tools.vmd.legacy import pose

ROOT = Path(__file__).resolve().parents[1]


class ModernClassicPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame_map = json.loads((ROOT / 'data/resharped_blade_frame_map.json').read_text())
        cls.policy = json.loads((ROOT / 'data/modern_classic_policy.json').read_text())
        cls.slots = json.loads((ROOT / 'data/bake_slots.json').read_text())['slots']
        legacy = json.loads((ROOT / 'data/legacy_motion_map.json').read_text())
        cls.combos = {entry['name']: entry for entry in legacy['entries']}
        cls.modern = by_id(cls.frame_map)
        cls.slot_by_name = {slot['name']: slot for slot in cls.slots}

    def assert_key_pose(self, key, expected, msg):
        position, rotation = expected
        for actual, wanted in zip(key.position, position):
            self.assertAlmostEqual(actual, wanted, places=5, msg=f'{msg} position')
        dot = abs(sum(a * b for a, b in zip(key.rotation, rotation)))
        self.assertGreater(dot, 1.0 - 1e-5, msg=f'{msg} rotation')

    def test_policy_ids_are_real_pinned_resharped_consumers(self):
        for family in self.policy['families']:
            for combo_id in family['modern_ids'] + family.get('shared_with', []):
                self.assertIn(combo_id, self.modern, f"{family['name']}: {combo_id}")

    def test_shared_and_independent_claims_match_atlas_topology(self):
        for family in self.policy['families']:
            external = external_consumers(self.frame_map, family['modern_ids'])
            external_ids = {entry['id'] for entry in external}
            if family['policy'] == 'INDEPENDENT_INTERPRETATION':
                self.assertEqual(external_ids, set(), family['name'])
            elif family['policy'] == 'SHARED_SLOT_INTERPRETATION':
                declared = set(family['shared_with'])
                self.assertTrue(declared, family['name'])
                self.assertTrue(
                    declared & external_ids,
                    f"{family['name']} declared no actually overlapping consumer; got {sorted(external_ids)}",
                )
            else:
                self.fail(f"Unexpected modern-family policy {family['policy']}")

    def test_policy_bake_slots_are_explicit_interpretations(self):
        valid = {'CLASSIC_RESTORATION', 'CLASSIC_INTERPRETATION'}
        for slot in self.slots:
            self.assertIn(slot.get('adaptation'), valid, slot['name'])
        for family in self.policy['families']:
            for slot_name in family['bake_slots']:
                slot = self.slot_by_name[slot_name]
                self.assertEqual(slot['adaptation'], 'CLASSIC_INTERPRETATION', slot_name)

    def test_bake_windows_do_not_overwrite_each_other(self):
        for i, left in enumerate(self.slots):
            for right in self.slots[i + 1:]:
                count = overlap_frames(left, right)
                self.assertEqual(
                    count,
                    0,
                    f"bake windows overlap: {left['name']} and {right['name']} share {count} frames",
                )

    def test_void_slash_is_a_dedicated_two_stage_interpretation(self):
        family = next(item for item in self.policy['families'] if item['name'] == 'void_slash')
        window = family_window(self.frame_map, family['modern_ids'])
        self.assertEqual(window, {'start': 2200, 'end': 2299})

        attack = self.slot_by_name['Void Slash']
        sheath = self.slot_by_name['Void Slash sheath']
        self.assertEqual((attack['start'], attack['end'], attack['legacy']), (2200, 2277, 'SlashDim'))
        self.assertEqual(attack['attack_offset'], 24)
        self.assertEqual((sheath['start'], sheath['end'], sheath['legacy']), (2278, 2299, 'Noutou'))
        self.assertEqual(sheath['legacy_entry_delay_ticks'], 5)
        self.assertEqual(timeout_target(attack, self.combos), 'none')
        # r32's Noutou state itself terminates to None; the +5 source clock
        # offset is represented by this slot's legacy_entry_delay_ticks.
        self.assertEqual(timeout_target(sheath, self.combos), 'none')

    def test_encoded_void_sheath_uses_full_source_timed_noutou_then_neutral(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            report = {entry['slot']: entry for entry in generate(output)}
            motion = decode((output / 'assets/slashblade/combostate/motion.vmd').read_bytes())
            keys = {(key.bone, key.frame): key for key in motion.keys}

            self.assertEqual(report['Void Slash']['adaptation'], 'CLASSIC_INTERPRETATION')
            self.assertEqual(report['Void Slash']['recovery'], 2236)
            self.assertEqual(report['Void Slash sheath']['adaptation'], 'CLASSIC_INTERPRETATION')
            self.assertEqual(report['Void Slash sheath']['recovery'], 2293)
            self.assertEqual(report['Void Slash sheath']['timeout_target'], 'none')

            for bone, is_sheath in (('hardpointA', False), ('hardpointB', True)):
                self.assert_key_pose(
                    keys[(bone, 2278)],
                    pose(self.combos['Noutou'], 0, is_sheath),
                    f'Void sheath start {bone}',
                )
                self.assert_key_pose(
                    keys[(bone, 2282)],
                    pose(self.combos['Noutou'], 4 / 9, is_sheath),
                    f'Void sheath mid {bone}',
                )
                self.assert_key_pose(
                    keys[(bone, 2287)],
                    pose(self.combos['Noutou'], 1, is_sheath),
                    f'Void sheath final swing pose {bone}',
                )
                self.assert_key_pose(
                    keys[(bone, 2292)],
                    pose(self.combos['Noutou'], 1, is_sheath),
                    f'Void sheath hold {bone}',
                )
                self.assert_key_pose(
                    keys[(bone, 2293)],
                    pose(self.combos['None'], 0, is_sheath),
                    f'Void sheath timeout {bone}',
                )


if __name__ == '__main__':
    unittest.main()
