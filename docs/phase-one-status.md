# Phase-one status

## Source/resource implementation: COMPLETE

For the pinned Minecraft 1.20.1 + SlashBlade: Resharped 1.9.65 target, the resource-pack-only implementation has reached its source-complete boundary.

`source-complete` means every phase-one visual subsystem has one of two outcomes:

1. an implemented resource path in the generated pack; or
2. a source-proven boundary that cannot be changed independently by an ordinary resource pack.

It does **not** mean visual acceptance has been completed in Minecraft. `runtime_complete` remains false until the candidate ZIP is actually compared in game.

The machine-readable status is `data/phase_one_scope.json`; CI runs `scripts/audit_phase_one.py` and fails if a required subsystem becomes unclassified.

## Implemented resource paths

- Classic r32 blade/saya procedural motion is sampled offline and baked into Resharped's fixed `combostate/motion.vmd` atlas.
- All modern motion regions consumed from that atlas are filled; direct legacy families are marked Classic Restoration and modern/shared semantic families are explicitly marked Classic Interpretation.
- `NONE` / `STANDBY` frames 0..1 contain the retargeted r32 neutral active-layer weapon pose.
- The generated player PMD/VMD uses the inspected Resharped missing-bone `return value0` path to suppress its custom skeletal SlashBlade pose while preserving the incoming player transform.
- Normal `EntitySlashEffect` art is replaced by a generated narrow classic trail adapter.
- Drive/Wave visual art uses a baked r32 procedural prism through Resharped's fixed effect-resource contract.
- Judgement Cut's installed `slashdim.obj/png` is left untouched because the modern and r32 Git blobs are already identical.
- First-person attacks see the same generated blade/saya VMD used by third person.
- The build is deterministic, validated, contains no Java/classes/runtime scripts/datapack logic, and CI emits the normal Resource Pack ZIP.

## Source-proven resource-pack ceilings

- The r32 first-person camera-relative hold matrix and Projectile Barrier FPV branch are Java renderer behavior. The pinned Resharped first-person renderer resets the incoming pose to identity and applies its own matrix, so item-model `firstperson_*` JSON cannot replace it.
- DEFAULT / PSO2 / NINJA back/offhand carry transforms are hard-coded by Resharped `renderStandbyBlade()`, not driven by the motion VMD.
- r32 explicitly restarts Minecraft's vanilla swing clock for accepted combos. A resource pack cannot set `swinging`, `swingTime` or `attackAnim`; therefore the player-body adapter intentionally promises pose passthrough, **not** an exact recreation of the r32 vanilla-arm swing event sequence.
- r32's dynamic blade afterimage copy loop, Projectile Barrier trail branch, live blur alpha/progress, runtime combo branching, hit logic, movement and cancel/invulnerability behavior require code.
- A universal 1.12.2 model-scale correction is not safely expressible through the shared VMD for arbitrary custom blade models; global geometry edits would change unrelated contexts and third-party blades.

## What remains

Only Minecraft runtime acceptance remains for phase one:

- blade/hand/sheath alignment with representative models;
- A1–A5 and air/special transition feel at normal and earliest input timing;
- first-person visibility and camera clipping;
- generated trail/Drive effect orientation and timing;
- crouch/walk/jump/custom model sampling;
- remote-player observation/multiplayer;
- restart/resource activation behavior.

These are observational release gates. They cannot be truthfully converted into source tests. Until those checks are run, the artifact is a **source-complete release candidate**, not a verified stable release.
