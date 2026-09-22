import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "first_person_render_contract.json"


class FirstPersonContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text())

    def test_pinned_sources(self):
        self.assertEqual(
            self.data["legacy"]["commit"],
            "ba1ef8604c0971f68336b882b42a868df7f32f0b",
        )
        self.assertEqual(
            self.data["target"]["commit"],
            "6e2a0a092fb794d7ea56fd83452869674f3ab1c7",
        )
        self.assertTrue(self.data["target"]["first_person_file"].endswith("BladeFirstPersonRender.java"))

    def test_target_discards_incoming_item_transform(self):
        ops = self.data["target"]["normal_operations"]
        self.assertEqual(ops[0], ["reset_current_pose_to_identity"])
        self.assertFalse(self.data["target"]["incoming_item_display_transform_survives"])
        self.assertEqual(
            self.data["resource_pack_classification"]["use_item_model_firstperson_display_to_override_slashblade_hold"],
            "INEFFECTIVE_ON_PINNED_TARGET",
        )

    def test_legacy_has_runtime_only_fpv_branches(self):
        normal = self.data["legacy"]["normal_old_style_operations"]
        barrier = self.data["legacy"]["barrier_old_style_operations"]
        self.assertNotEqual(normal, barrier)
        self.assertEqual(normal[1], ["translate", -0.35, -0.1, -0.8])
        self.assertEqual(barrier[1], ["translate", 0.0, 0.1, -0.8])
        self.assertEqual(normal[2], ["rotate_axis_degrees", -3.0, 1.0, 0.0, 0.0])
        self.assertEqual(barrier[2], ["rotate_axis_degrees", -30.0, 1.0, 0.0, 0.0])

    def test_resource_pack_boundary_is_explicit(self):
        policy = self.data["resource_pack_classification"]
        self.assertEqual(
            policy["classic_attack_blade_sheath_motion_visible_in_first_person"],
            "SUPPORTED",
        )
        for key in (
            "replace_static_first_person_camera_relative_hold_transform_only",
            "restore_legacy_projectile_barrier_first_person_branch",
            "restore_legacy_pitch_sync_policy",
        ):
            self.assertEqual(policy[key], "IMPOSSIBLE_RESOURCE_PACK_ONLY")
        self.assertEqual(
            policy["global_model_or_vmd_offset_as_fpv_fix"],
            "REJECTED_BECOMES_THIRD_PERSON_REGRESSION",
        )

    def test_pack_does_not_ship_misleading_item_display_override(self):
        # The pinned SlashBlade custom first-person renderer resets its incoming
        # PoseStack to identity. Shipping a firstperson_* display JSON and calling
        # it an FPV restoration would therefore be misleading.
        path = ROOT / "pack" / "assets" / "slashblade" / "models" / "item" / "slashblade.json"
        self.assertFalse(path.exists())

    def test_docs_record_hard_ceiling(self):
        research = (ROOT / "docs" / "research" / "first-person-rendering.md").read_text()
        limitations = (ROOT / "docs" / "limitations.md").read_text()
        readme = (ROOT / "README.md").read_text()
        for text in (research, limitations, readme):
            self.assertIn("IMPOSSIBLE_RESOURCE_PACK_ONLY", text)
        self.assertIn("identity", research)
        self.assertIn("first-person", research.lower())


if __name__ == "__main__":
    unittest.main()
