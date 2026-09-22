import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PlayerPoseAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / "data" / "player_pose_adapter_contract.json").read_text())

    def test_contract_pins_missing_bone_semantics(self):
        target = self.contract["target"]
        self.assertEqual(target["missing_bone_behavior"], "return_value0")
        self.assertEqual(target["motion_layer_index"], 0)
        self.assertTrue(target["motion_layer_is_installed_on_blade_motion_event"])
        self.assertTrue(target["pmd_is_static_lazy_cached"])

    def test_generated_pmd_contains_only_unknown_adapter_bone(self):
        from scripts.generate_motions import passthrough_pmd

        data = passthrough_pmd()
        self.assertIn(b"classic_root", data)
        forbidden = (
            b"body",
            b"head",
            b"left arm",
            b"right arm",
            b"left leg",
            b"right leg",
            b"leftArm",
            b"rightArm",
            b"leftLeg",
            b"rightLeg",
        )
        for name in forbidden:
            self.assertNotIn(name, data)

    def test_generated_player_vmd_only_targets_adapter_bone(self):
        from scripts.generate_motions import generate
        from tools.vmd.codec import decode

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            generate(root)
            motion = decode((root / "assets/slashblade/model/pa/player_motion.vmd").read_bytes())
        self.assertEqual(set(motion.tracks()), {"classic_root"})

    def test_adapter_never_claims_recovered_legacy_skeleton(self):
        self.assertFalse(self.contract["legacy"]["full_body_vmd_present"])
        self.assertEqual(
            self.contract["limitations"]["recovered_r32_full_body_animation"],
            "NOT_AVAILABLE_IN_SOURCE",
        )
        self.assertEqual(
            self.contract["pack_adapter"]["classification"],
            "RESOURCE_ONLY_PASSTHROUGH_ADAPTER",
        )

    def test_research_doc_explains_value0_path(self):
        text = (ROOT / "docs" / "research" / "player-pose-adapter.md").read_text()
        self.assertIn("value0", text)
        self.assertIn("classic_root", text)
        self.assertIn("IMPOSSIBLE_RESOURCE_PACK_ONLY", text)
        self.assertIn("NOT AVAILABLE IN SOURCE", text)


if __name__ == "__main__":
    unittest.main()
