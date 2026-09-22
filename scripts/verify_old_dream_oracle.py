"""Cross-check the r32 procedural bake source against Old Dream Reforged.

This is a development/CI verifier only; it is not shipped in the resource pack.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.vmd.legacy import dynamic as r32_dynamic, progress as r32_progress
from tools.vmd.old_dream_oracle import (
    ALIASES,
    SOURCE_COMMIT,
    SOURCE_REPO,
    dynamic as oracle_dynamic,
    parameters,
    progress as oracle_progress,
)

T_SAMPLES = (-0.2, 0.0, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.2)
MATRIX_SAMPLES = (0.0, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0)
TOLERANCE = 1e-10


def verify():
    source = json.loads((ROOT / 'data/legacy_motion_map.json').read_text())
    combos = {entry['name']: entry for entry in source['entries']}
    missing = sorted(set(ALIASES) - set(combos))
    parameter_mismatches = []
    max_progress_error = 0.0
    max_matrix_error = 0.0

    for name in sorted(ALIASES):
        if name not in combos:
            continue
        combo = combos[name]
        actual = (
            combo['scabbard'],
            float(combo['amplitude']),
            float(combo['direction']),
            int(combo['reset_ticks']),
        )
        expected = parameters(name)
        if actual != expected:
            parameter_mismatches.append({'move': name, 'r32': actual, 'oracle': expected})

        for t in T_SAMPLES:
            max_progress_error = max(
                max_progress_error,
                abs(r32_progress(t, name) - oracle_progress(t, name)),
            )

        for sheath in (False, True):
            for t in MATRIX_SAMPLES:
                a = r32_dynamic(combo, t, sheath)
                b = oracle_dynamic(name, t, sheath)
                for row in range(4):
                    for col in range(4):
                        max_matrix_error = max(max_matrix_error, abs(a[row][col] - b[row][col]))

    report = {
        'oracle_repo': SOURCE_REPO,
        'oracle_commit': SOURCE_COMMIT,
        'canonical_source': source['commit'],
        'moves_compared': len(ALIASES),
        'missing_moves': missing,
        'parameter_mismatches': parameter_mismatches,
        'max_progress_error': max_progress_error,
        'max_dynamic_matrix_error': max_matrix_error,
        'tolerance': TOLERANCE,
    }
    return report


def main():
    report = verify()
    print(json.dumps(report, indent=2))
    failed = (
        report['missing_moves']
        or report['parameter_mismatches']
        or report['max_progress_error'] > TOLERANCE
        or report['max_dynamic_matrix_error'] > TOLERANCE
    )
    raise SystemExit(1 if failed else 0)


if __name__ == '__main__':
    main()
