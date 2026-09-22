import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StandbyCarryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / "data" / "standby_carry_contract.json").read_text())
        cls.frame_map = json.loads((ROOT / "data" / "resharped_blade_frame_map.json").read_text())["entries"]

    def test_old_and_modern_legacy_ordinals_line_up(self):
        old = self.contract["legacy"]["standby_render_type_ordinals"]
        modern = self.contract["target"]["carry_type_ordinals"]
        for name in ("NONE", "DEFAULT", "PSO2", "NINJA"):
            self.assertEqual(old[name], modern[name])

    def test_none_and_standby_share_motion_frames(self):
        rows = {r["combo"]: r for r in self.frame_map}
        for name in ("NONE", "STANDBY"):
            self.assertEqual(rows[name]["resource"], "slashblade:combostate/motion.vmd")
            self.assertEqual((rows[name]["start"], rows[name]["end"]), (0, 1))

    def test_generated_frame_zero_is_classic_none_pose(self):
        from scripts.generate_motions import generate
        from tools.vmd.codec import decode
        from tools.vmd.legacy import pose

        legacy = json.loads((ROOT / "data" / "legacy_motion_map.json").read_text())
        none = next(row for row in legacy["entries"] if row["name"] == "None")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            generate(root)
            motion = decode((root / "assets/slashblade/combostate/motion.vmd").read_bytes())
            tracks = motion.tracks()
        for bone, sheath in (("hardpointA", False), ("hardpointB", True)):
            key = next(k for k in tracks[bone] if k.frame == 0)
            expected_pos, expected_rot = pose(none, 0, sheath)
            for actual, expected in zip(key.position, expected_pos):
                self.assertAlmostEqual(actual, expected, places=5)
            dot = abs(sum(a * b for a, b in zip(key.rotation, expected_rot)))
            self.assertAlmostEqual(dot, 1.0, places=5)

    def test_back_carry_is_not_misclassified_as_vmd(self):
        policy = self.contract["resource_pack_classification"]
        self.assertEqual(policy["main_hand_none_standby_blade_sheath_pose"], "SUPPORTED_VIA_MOTION_VMD")
        for key in (
            "classic_default_back_carry_transform",
            "classic_pso2_back_carry_transform",
            "classic_ninja_back_carry_transform",
        ):
            self.assertEqual(policy[key], "IMPOSSIBLE_RESOURCE_PACK_ONLY")
        self.assertTrue(self.contract["target"]["back_carry_transform_is_java_hardcoded"])

    def test_research_doc_records_distinction(self):
        text = (ROOT / "docs" / "research" / "standby-carry-rendering.md").read_text()
        self.assertIn("SUPPORTED_VIA_MOTION_VMD", text)
        self.assertIn("IMPOSSIBLE_RESOURCE_PACK_ONLY", text)
        self.assertIn("renderStandbyBlade", text)


if __name__ == "__main__":
    unittest.main()
