import json
from pathlib import Path
import unittest

from tools.vmd.legacy import dynamic as r32_dynamic, progress as r32_progress
from tools.vmd.old_dream_oracle import ALIASES, dynamic as oracle_dynamic, parameters, progress as oracle_progress

ROOT = Path(__file__).resolve().parents[1]


class OldDreamOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads((ROOT / 'data/legacy_motion_map.json').read_text())
        cls.combos = {entry['name']: entry for entry in data['entries']}

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


if __name__ == '__main__':
    unittest.main()
