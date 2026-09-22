"""Independent Old Dream Reforged oracle for classic blade/saya motion math.

This module is validation-only. Runtime pack generation continues to use the pinned
official SlashBlade 1.12.2 r32 source as canonical provenance.

Reference:
  rianfalltwilight-lab/seac-slashblade-old-dream-reforged
  commit a6b8cf5e3b5b3f270212a47b8d373a95f6a31af3
  LegacyMove.java / LegacyBladePose.java

Old Dream Reforged is MIT-licensed code. See THIRD_PARTY_NOTICES.md.
No code in this module is required by the shipped resource pack.
"""
from .transforms import chain, identity, quaternion, translation as T, rotate as R, scale as S

SOURCE_REPO = "rianfalltwilight-lab/seac-slashblade-old-dream-reforged"
SOURCE_COMMIT = "a6b8cf5e3b5b3f270212a47b8d373a95f6a31af3"

# Values from Old Dream Reforged LegacyMove.java at SOURCE_COMMIT:
# (uses_scabbard, swing_amplitude, swing_direction, reset_ticks)
MOVES = {
    "NONE": (True, 0.0, 0.0, 0),
    "SAYA1": (True, 200.0, 5.0, 20),
    "SAYA2": (True, -200.0, 5.0, 20),
    "BATTOU": (False, 240.0, 0.0, 12),
    "NOUTOU": (False, -210.0, 10.0, 5),
    "KIRIAGE": (False, 260.0, 70.0, 20),
    "KIRIOROSI": (False, -260.0, 90.0, 12),
    "SLASH_DIM": (False, -220.0, 10.0, 8),
    "IAI": (False, 240.0, 0.0, 20),
    "HIRA_TUKI": (False, 180.0, 180.0, 20),
    "SLASH_EDGE": (False, 240.0, 20.0, 12),
    "RETURN_EDGE": (False, 250.0, -160.0, 12),
    "S_IAI": (False, 240.0, 0.0, 12),
    "S_SLASH_EDGE": (False, 240.0, 20.0, 25),
    "S_RETURN_EDGE": (False, 250.0, -160.0, 25),
    "S_SLASH_BLADE": (False, 200.0, -315.0, 25),
    "A_SLASH_EDGE": (False, 240.0, 20.0, 25),
    "A_KIRIOROSI": (False, 200.0, -240.0, 25),
    "A_KIRIAGE": (False, 240.0, -70.0, 12),
    "A_KIRIOROSI_FINISH": (False, 200.0, -270.0, 25),
    "RAPID_SLASH": (False, 600.0, -380.0, 12),
    "RAPID_SLASH_END": (False, 240.0, 20.0, 12),
    "RISING_STAR": (False, 250.0, -160.0, 12),
    "HELM_BRAKER": (False, 200.0, -270.0, 25),
    "HELM_LANDING": (False, 200.0, -270.0, 6),
    "CALIBUR": (False, 600.0, -380.0, 25),
    "FORCE1": (False, 300.0, -230.0, 25),
    "FORCE2": (False, 250.0, -30.0, 25),
    "FORCE3": (True, 200.0, 5.0, 20),
    "FORCE4": (True, -200.0, 5.0, 20),
    "FORCE5": (False, 240.0, 0.0, 12),
    "FORCE6": (False, 200.0, -270.0, 25),
    "STINGER": (False, 180.0, 180.0, 20),
}

# r32 source spelling -> Old Dream Reforged spelling.
ALIASES = {
    "None": "NONE",
    "Saya1": "SAYA1",
    "Saya2": "SAYA2",
    "Battou": "BATTOU",
    "Noutou": "NOUTOU",
    "Kiriage": "KIRIAGE",
    "Kiriorosi": "KIRIOROSI",
    "SlashDim": "SLASH_DIM",
    "Iai": "IAI",
    "HiraTuki": "HIRA_TUKI",
    "SlashEdge": "SLASH_EDGE",
    "ReturnEdge": "RETURN_EDGE",
    "SIai": "S_IAI",
    "SSlashEdge": "S_SLASH_EDGE",
    "SReturnEdge": "S_RETURN_EDGE",
    "SSlashBlade": "S_SLASH_BLADE",
    "ASlashEdge": "A_SLASH_EDGE",
    "AKiriorosi": "A_KIRIOROSI",
    "AKiriage": "A_KIRIAGE",
    "AKiriorosiFinish": "A_KIRIOROSI_FINISH",
    "RapidSlash": "RAPID_SLASH",
    "RapidSlashEnd": "RAPID_SLASH_END",
    "RisingStar": "RISING_STAR",
    "HelmBraker": "HELM_BRAKER",
    "Calibur": "CALIBUR",
    "Force1": "FORCE1",
    "Force2": "FORCE2",
    "Force3": "FORCE3",
    "Force4": "FORCE4",
    "Force5": "FORCE5",
    "Force6": "FORCE6",
    "Stinger": "STINGER",
}


def oracle_name(r32_name):
    try:
        return ALIASES[r32_name]
    except KeyError as exc:
        raise KeyError(f"{r32_name!r} has no Old Dream oracle mapping") from exc


def parameters(r32_name):
    return MOVES[oracle_name(r32_name)]


def progress(t, r32_name):
    """Old Dream Reforged LegacyBladePose.progress, expressed with r32 names."""
    value = min(1.0, max(0.0, t) * 1.2)
    name = oracle_name(r32_name)
    if name in ("IAI", "S_IAI"):
        return 1.0 - abs(value - 0.5) * 2.0
    if name in ("STINGER", "HIRA_TUKI", "HELM_LANDING"):
        return 1.0
    return 1.0 - (1.0 - value) * (1.0 - value)


def dynamic(r32_name, t, sheath=False):
    """Return the procedural swing transform, excluding outer model scaling.

    Keeping model scale out of this comparison is intentional: the pure resource
    pack cannot encode bone scale in VMD, so Resharped's installed model scale stays
    authoritative. This validates the classic motion math itself.
    """
    name = oracle_name(r32_name)
    scabbard, amplitude, direction, _ = MOVES[name]
    if name == "NONE" or (sheath and not scabbard):
        return identity()

    value = progress(t, r32_name)
    if amplitude < 0:
        value = 1.0 - value

    pre = T(0, 0, -26) if name in ("STINGER", "HIRA_TUKI") and not sheath else identity()

    if name == "KIRIOROSI" and not sheath:
        return chain(
            pre,
            R("x", -20), R("z", 30), T(0, 0, -8),
            R("y", -(90 - direction)),
            R("z", (1 - value) * 90),
            T((1 - value) * 10, (1 - value) * -5, 0),
            T(-10, -8, 0),
            R("z", -abs(amplitude)),
            T(10, 8, 0),
            R("y", 180),
        )

    if direction < 0 and not sheath:
        return chain(
            pre,
            R("x", -20), R("z", 30), T(0, 0, -12),
            R("y", -(90 + direction)),
            R("z", (1 - value) * 240),
            T(-10, -8, 0),
            R("z", -value * abs(amplitude)),
            T(10, 8, 0),
        )

    return chain(
        pre,
        R("x", -20 * value),
        R("z", 30 * value),
        R("y", -value * (90 - direction)),
        T(-10, -8, 0),
        R("z", -value * abs(amplitude)),
        T(10, 8, 0),
    )


def runtime_matrix(r32_name, t, sheath=False):
    """Full Old Dream runtime blade/saya matrix, including its 0.095 model scale."""
    return chain(
        T(0.25, 0.4, -0.5),
        S(0.075),
        R("x", 60),
        R("z", -20),
        R("y", 90),
        dynamic(r32_name, t, sheath),
        S(0.095),
        R("z", -90),
    )


def normalized_motion_matrix(r32_name, t, sheath=False):
    """Old Dream motion normalized for Resharped's fixed installed model scale.

    Old SlashBlade applied a 0.075 outer scale and a 0.095 model-local scale.
    Resharped's VMD hardpoints cannot carry scale, so the baker preserves the
    modern model scale and retargets only position/rotation. This removes the
    old outer scale after applying the procedural transform, matching the
    normalization used by the resource-pack baker without borrowing its math.
    """
    return chain(
        T(0.25, 0.4, -0.5),
        S(0.075),
        R("x", 60),
        R("z", -20),
        R("y", 90),
        dynamic(r32_name, t, sheath),
        S(1.0 / 0.075),
        R("z", -90),
    )


def retarget_pose(r32_name, t, sheath=False):
    """Independent oracle pose in Resharped hardpoint coordinates."""
    m = chain(
        S(-1, 1, 1),
        R("z", -180),
        S(8),
        T(0, -1.5, 0),
        normalized_motion_matrix(r32_name, t, sheath),
        S(0.125),
        S(-1, 1, 1),
    )
    return tuple(m[i][3] for i in range(3)), quaternion(m)
