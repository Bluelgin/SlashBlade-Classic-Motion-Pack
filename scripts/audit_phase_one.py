"""Fail CI if phase-one source scope regresses to an unclassified/planned state."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    scope = json.loads((ROOT / "data" / "phase_one_scope.json").read_text())
    allowed = set(scope["allowed_terminal_statuses"])
    systems = scope["systems"]
    if not scope.get("source_complete"):
        raise SystemExit("phase one is not marked source-complete")
    if scope.get("runtime_complete"):
        raise SystemExit("runtime_complete must remain false until Minecraft acceptance is actually run")
    if not systems:
        raise SystemExit("phase-one systems list is empty")
    ids = [row["id"] for row in systems]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate phase-one system id")
    invalid = [(row["id"], row["status"]) for row in systems if row["status"] not in allowed]
    if invalid:
        raise SystemExit(f"non-terminal/unclassified phase-one status: {invalid}")

    required = {
        "ground_combo_blade_saya",
        "air_combo_blade_saya",
        "special_move_blade_saya",
        "main_hand_none_standby",
        "player_body_override_removal",
        "r32_vanilla_swing_clock_restart",
        "normal_slash_trail",
        "legacy_blade_afterimage_copy_count",
        "drive_projectile_visual",
        "judgement_cut_dimension_asset",
        "first_person_attack_motion",
        "first_person_idle_hold_wrapper",
        "first_person_projectile_barrier_branch",
        "back_offhand_carry_default_pso2_ninja",
        "runtime_combo_branch_selection",
        "damage_hitbox_velocity_cancel_invulnerability",
        "legacy_dynamic_projectile_barrier_trail",
        "exact_global_legacy_model_scale_for_all_custom_blades",
        "resource_pack_zip",
    }
    missing = sorted(required - set(ids))
    if missing:
        raise SystemExit(f"missing phase-one classification: {missing}")

    # Cross-contract invariants: these are the hard boundaries most likely to be
    # accidentally overclaimed in future documentation.
    fp = json.loads((ROOT / "data" / "first_person_render_contract.json").read_text())
    if fp["resource_pack_classification"]["replace_static_first_person_camera_relative_hold_transform_only"] != "IMPOSSIBLE_RESOURCE_PACK_ONLY":
        raise SystemExit("first-person wrapper ceiling changed without updating phase-one scope")
    carry = json.loads((ROOT / "data" / "standby_carry_contract.json").read_text())
    if carry["resource_pack_classification"]["main_hand_none_standby_blade_sheath_pose"] != "SUPPORTED_VIA_MOTION_VMD":
        raise SystemExit("main-hand standby support contract regressed")
    pose = json.loads((ROOT / "data" / "player_pose_adapter_contract.json").read_text())
    if pose["target"]["missing_bone_behavior"] != "return_value0":
        raise SystemExit("player passthrough assumption changed")

    # Every authored VMD bake slot must already have a terminal mapping label.
    slots = json.loads((ROOT / "data" / "bake_slots.json").read_text())["slots"]
    for slot in slots:
        if slot.get("status") not in {"EXACT", "REMAP", "APPROXIMATE"}:
            raise SystemExit(f"unclassified bake slot: {slot['name']}")
        if slot.get("adaptation") not in {"CLASSIC_RESTORATION", "CLASSIC_INTERPRETATION"}:
            raise SystemExit(f"unclassified adaptation: {slot['name']}")

    # Source metadata must tell the same truth as the machine-readable gate.
    root_readme = (ROOT / "README.md").read_text()
    pack_readme = (ROOT / "pack" / "README.md").read_text()
    if root_readme != pack_readme:
        raise SystemExit("root README and packaged README are out of sync")
    for required_text in (
        "source-complete release candidate",
        "Minecraft runtime verification pending",
        "IMPOSSIBLE_RESOURCE_PACK_ONLY",
    ):
        if required_text not in root_readme:
            raise SystemExit(f"README is missing phase-one status text: {required_text}")
    mcmeta = json.loads((ROOT / "pack" / "pack.mcmeta").read_text())
    description = mcmeta["pack"]["description"]
    if "Source-complete RC" not in description or "runtime verification pending" not in description:
        raise SystemExit("pack.mcmeta does not describe the source-complete/runtime-pending state")

    print(f"phase-one source audit: PASS ({len(systems)} systems, {len(slots)} VMD bake slots)")
    print("runtime acceptance: PENDING (must be performed in Minecraft)")


if __name__ == "__main__":
    main()