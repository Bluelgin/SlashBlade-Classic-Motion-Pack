import json
from pathlib import Path
import tempfile
import unittest

from scripts.generate_motions import generate
from tools.vmd.codec import decode
from tools.vmd.legacy import dynamic as r32_dynamic, progress as r32_progress
from tools.vmd.old_dream_oracle import (
    ALIASES,
    dynamic as oracle_dynamic,
    normalized_motion_matrix,
    parameters,
    progress as oracle_progress,
    retarget_pose,
)
from tools.vmd.transforms import chain, from_pose, translation as T, scale as S, rotate as R

ROOT = Path(__file__).resolve().parents[1]


class OldDreamOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads((ROOT / 'data/legacy_motion_map.json').read_text())
        cls.combos = {entry['name']: entry for entry in data['entries']}
        cls.slots = json.loads((ROOT / 'data/bake_slots.json').read_text())['slots']

    def test_shared_move_metadata_matches_reference(self):
        # Old Dream Reforged independently reimplemented the classic move table.
        # Every overlapping r32 move should agree on scabbard use, amplitude,
        # direction and enum reset ticks. Two r32-only aliases are intentionally
        # outside this oracle: AerialRave and AKiriorosiB.
        missing = set(ALIASES) - set(self.combos)
        self.assertEqual(missing, set())
        for name in sorted(ALIASES):
            combo = self.combos[name]
            expected = parameters(name)
            actual = (
                combo['scabbard'],
                float(combo['amplitude']),
                float(combo['direction']),
                int(combo['reset_ticks']),
            )
            self.assertEqual(actual, expected, name)

    def test_progress_curve_matches_reference(self):
        for name in sorted(ALIASES):
            for t in (-0.2, 0.0, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.2):
                self.assertAlmostEqual(
                    r32_progress(t, name),
                    oracle_progress(t, name),
                    places=12,
                    msg=f'{name} @ {t}',
                )

    def test_dynamic_blade_and_sheath_matrices_match_reference(self):
        for name in sorted(ALIASES):
            combo = self.combos[name]
            for sheath in (False, True):
                for t in (0.0, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0):
                    actual = r32_dynamic(combo, t, sheath)
                    expected = oracle_dynamic(name, t, sheath)
                    for row in range(4):
                        for col in range(4):
                            self.assertAlmostEqual(
                                actual[row][col],
                                expected[row][col],
                                places=12,
                                msg=f'{name} sheath={sheath} t={t} [{row},{col}]',
                            )

    def test_generated_vmd_primary_swings_match_oracle(self):
        # Validate the encoded binary keys and then feed those decoded hardpoint
        # records through the same transform chain used by Resharped's blade layer.
        # This catches codec, handedness, quaternion and retargeting errors that a
        # source-level function-vs-function comparison can miss.
        #
        # Compound/multi-segment slots are intentionally excluded because a single
        # Old Dream move is not their complete semantic reference.
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            generate(output)
            motion = decode((output / 'assets/slashblade/combostate/motion.vmd').read_bytes())
            keys = {(key.bone, key.frame): key for key in motion.keys}

            compared = 0
            max_matrix_error = 0.0
            for slot in self.slots:
                name = slot['legacy']
                if name not in ALIASES or slot.get('segments') or 'second_legacy' in slot:
                    continue
                start = slot['start']
                end = min(slot['end'], slot['recovery_start'] - 1)
                attack_offset = slot.get('attack_offset', 0)
                swing_frames = slot.get('swing_frames', 9)
                active_end = min(end, start + attack_offset + swing_frames)
                if active_end < start:
                    continue

                for frame in range(start, active_end + 1):
                    t = max(0.0, frame - start - attack_offset) / swing_frames
                    t = min(1.0, t)
                    for bone, sheath in (('hardpointA', False), ('hardpointB', True)):
                        key = keys[(bone, frame)]

                        expected_pos, expected_rot = retarget_pose(name, t, sheath)
                        for actual, expected in zip(key.position, expected_pos):
                            self.assertAlmostEqual(
                                actual,
                                expected,
                                places=5,
                                msg=f'{slot["name"]} {bone} frame={frame} position',
                            )
                        # q and -q encode the same rotation, so compare absolute dot.
                        dot = abs(sum(a * b for a, b in zip(key.rotation, expected_rot)))
                        self.assertGreater(
                            dot,
                            1.0 - 1e-5,
                            msg=f'{slot["name"]} {bone} frame={frame} rotation',
                        )

                        reconstructed = chain(
                            T(0, 1.5, 0),
                            S(0.125),
                            R('z', 180),
                            S(-1, 1, 1),
                            from_pose(key.position, key.rotation),
                            S(-1, 1, 1),
                            S(8),
                        )
                        expected_matrix = normalized_motion_matrix(name, t, sheath)
                        for row in range(4):
                            for col in range(4):
                                error = abs(reconstructed[row][col] - expected_matrix[row][col])
                                max_matrix_error = max(max_matrix_error, error)
                                self.assertLessEqual(
                                    error,
                                    2e-5,
                                    msg=(
                                        f'{slot["name"]} {bone} frame={frame} '
                                        f'matrix[{row},{col}] error={error}'
                                    ),
                                )
                        compared += 1

            self.assertGreater(compared, 100)
            self.assertLessEqual(max_matrix_error, 2e-5)


if __name__ == '__main__':
    unittest.main()
