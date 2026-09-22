# SlashBlade Classic Motion Pack

Restore the classic SlashBlade 1.12.2/r32 motion language on SlashBlade: Resharped for Minecraft 1.20.1.

**v0.1.0 source-complete release candidate — Minecraft runtime verification pending.** Phase-one resource implementation is complete for the pinned target: every known visual subsystem is either implemented through ordinary resource-pack assets or classified from source as a hard `IMPOSSIBLE_RESOURCE_PACK_ONLY` / target-owned boundary. This is still **not** a verified stable release until the in-game acceptance checklist is run.

This is a resource pack, not a mod. It contains a source-derived classic blade/saya animation bake, a resource-only player-pose passthrough adapter and generated classic-style attack-effect adapters. It does **not** claim a recovered 1.12.2 skeletal animation atlas; official r32 implements its blade motions procedurally in Java and ships no full-body VMD/PMD animation set.

## Requirements

- Minecraft 1.20.1
- SlashBlade: Resharped and its normal dependencies, including its player-animation support
- Inspected target: Resharped **1.9.65**, commit `6e2a0a092fb794d7ea56fd83452869674f3ab1c7`

**No additional project-specific mod required.** No Java classes, Mixins, scripts, datapacks or executable code ship in the ZIP.

## Installation

1. Get `SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip` from the latest successful Actions artifact.
2. Put the ZIP into `.minecraft/resourcepacks/` without extracting it.
3. Enable it above other packs that override SlashBlade animation/effect resources.
4. Restart Minecraft, then enter a world and use SlashBlade.

Restart is required for a reliable test because Resharped caches the player PMD in a static lazy value. Restart after disabling the pack too; a live enable/disable cycle is not a valid comparison.

## Phase-one status

| Area | Result |
|---|---|
| Ground A chain | A1/A2 are source-derived Saya1/Saya2 restorations; A3–A5/A4 EX use the coherent r32 S-rank motion language fitted into modern fixed slots |
| Air / Upper / Rapid / Rising | Source-derived legacy move families baked into their modern windows; shared modern semantics are explicitly Classic Interpretation |
| Judgement / Void | Judgement blade motion uses classic SlashDim language; Void uses a dedicated SlashDim-like attack + Noutou sheath interpretation |
| B / C / Circle / Sakura / shared Drive-Wave slots | Explicit shared-slot Classic Interpretation; one VMD region must serve every modern caller |
| Main-hand `NONE` / `STANDBY` | `SUPPORTED_VIA_MOTION_VMD`; frames 0..1 contain the retargeted r32 active-layer neutral pose |
| Player body | Generated missing-bone PMD/VMD suppresses Resharped's custom skeletal SlashBlade pose and returns the incoming player transforms unchanged |
| r32 vanilla swing-clock restart | `IMPOSSIBLE_RESOURCE_PACK_ONLY`; pose passthrough is not a claim that every accepted modern combo restarts the old vanilla arm swing exactly |
| Normal slash light / `EntitySlashEffect` | Generated narrow classic trail adapter replaces modern `slash.obj/png` globally |
| Drive projectile visual | Generated r32 procedural prism baked to Resharped's `drive.obj` contract; neutral `ss.png` preserves runtime tint |
| Judgement Cut dimension art | Installed Resharped `slashdim.obj/png` Git blobs are already identical to r32; intentionally left untouched |
| First-person attack motion | Same generated blade/saya VMD is rendered by `LayerMainBlade`; subject to runtime clipping/alignment acceptance |
| First-person idle/hold wrapper | `IMPOSSIBLE_RESOURCE_PACK_ONLY`; Resharped resets the incoming pose and applies a hard-coded FPV matrix |
| Back/offhand DEFAULT / PSO2 / NINJA carry | `IMPOSSIBLE_RESOURCE_PACK_ONLY`; modern `renderStandbyBlade()` owns these Java transforms |
| Old dynamic blade afterimage loop / Projectile Barrier trail | `IMPOSSIBLE_RESOURCE_PACK_ONLY`; copy count, live progress/alpha/state branching are runtime renderer behavior |
| Gameplay | Resharped damage, hitboxes, movement, cancel windows, invulnerability, targeting and combo-state logic remain authoritative |

The ground classic chain starts with two **saya strikes**. The shared A3 region uses old `SIai`; the powered continuation can then read as `SSlashEdge → SReturnEdge → SSlashBlade`. Pure resource data cannot branch A3 between old Battou/SIai behavior based on historical rank/timing state, so shared modern branches are documented interpretations rather than mislabeled exact ports.

See the machine-readable phase gate in [`data/phase_one_scope.json`](data/phase_one_scope.json) and the human summary in [`docs/phase-one-status.md`](docs/phase-one-status.md). CI runs `scripts/audit_phase_one.py` so new source work cannot silently reintroduce an unclassified phase-one subsystem.

## Why the pack is built this way

Official r32 has no VMD attack atlas to copy. Its visible blade/saya motion is generated in `LayerSlashBlade.java`. The pack therefore follows this path:

```text
r32 procedural Java formulas
        ↓ offline sampling
blade + sheath transforms
        ↓ retarget to Resharped hardpoints
fixed modern frame windows
        ↓
combostate/motion.vmd
        ↓
normal Resource Pack ZIP
```

The original source is authoritative. The independent modern project Old Dream Reforged is used only as a second matrix/procedural oracle where its legacy behavior overlaps; it is not a runtime dependency and no Java renderer from it ships here.

## Player-body strategy

r32 restarts Minecraft's normal swing clock and renders SlashBlade's weapon layer separately; it does not ship a recoverable full-body skeletal clip. Resharped, by contrast, starts a custom `VmdAnimation` on blade motions.

The generated `alex.pmd` and `player_motion.vmd` contain only an unknown `classic_root` bone. In the pinned Resharped `VmdAnimation`, missing player bones fall through to `return value0`, so normal player parts receive their incoming transforms rather than the modern custom SlashBlade skeletal pose. This is intentional passthrough architecture, not a placeholder.

A resource pack cannot reproduce r32's Java `doSwingItem` state mutation for every accepted combo, change Resharped animation-layer priority, or remove every Java user-pose/root rotation. See [`docs/research/player-pose-adapter.md`](docs/research/player-pose-adapter.md).

## First-person and carry ceilings

r32's old-style first-person view is Java-driven: it applies its own camera-relative matrix, has a separate Projectile Barrier branch and controls pitch/blur behavior. The pinned Resharped `BladeFirstPersonRender` resets its incoming `PoseStack` to identity before applying a fixed modern transform. Consequently a `models/item/slashblade.json` `firstperson_*` display override cannot restore the r32 hold view. The classic **attack VMD remains visible** inside that wrapper. See [`docs/research/first-person-rendering.md`](docs/research/first-person-rendering.md).

Main-hand standby is different: Resharped `NONE` and `STANDBY` use frames 0..1 of `combostate/motion.vmd`, and those frames are already the retargeted r32 neutral weapon pose. Back/offhand carry goes through Java `renderStandbyBlade()` and cannot be independently replaced by this pack. See [`docs/research/standby-carry-rendering.md`](docs/research/standby-carry-rendering.md).

## Effect ceiling

The pack can replace fixed effect meshes/textures but not their Java entity renderers. For normal slash effects, Resharped still owns spawn timing, lifetime, progress rotation, size, rank passes and color. Drive and Judgement Cut likewise retain modern runtime choreography. Generated effect assets are therefore designed to read as classic under those fixed transforms; they are not a claim that r32's blade-attached trail/afterimage Java loop is executing on 1.20.1.

Detailed mappings: [`docs/mapping/classic-effect-adaptation.md`](docs/mapping/classic-effect-adaptation.md), [`docs/mapping/legacy-to-resharped.md`](docs/mapping/legacy-to-resharped.md), and [`docs/mapping/modern-classic-interpretation.md`](docs/mapping/modern-classic-interpretation.md).

## Runtime verification

Source analysis, old-source extraction, independent oracle comparisons, decoded-VMD matrix reconstruction, frame coverage, effect-resource checks, format validation and deterministic builds are automated. They cannot judge feel, clipping or camera composition.

Before a stable release, run [`docs/testing-checklist.md`](docs/testing-checklist.md): compare r32/control/candidate footage, test A1–A5 and all air/special families, earliest combo inputs, first person, crouch/walk/jump, custom blade models, generated effects and remote players. Hard resource-pack ceilings documented above are not runtime bugs to “fix” with a global model offset.

## Build

Python 3.10+; no third-party Python packages:

```sh
python scripts/verify_old_dream_oracle.py
python scripts/audit_phase_one.py
python -m unittest discover -s tests -v
python scripts/build_pack.py
python scripts/validate_pack.py dist/SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip
```

The build regenerates all shipped VMD/PMD/effect resources, writes the original project icon, validates the pack and creates a deterministic ZIP with `pack.mcmeta` at its root. Development details: [`docs/development.md`](docs/development.md).

## Credits and license

Classic procedural reference: Furia / flammpfeil, SlashBlade `mc1.12-r32`, official `1.12.2` branch. Modern resource contracts: MMF-Group / 0999312, SlashBlade: Resharped. Independent validation reference: Old Dream Reforged.

Project tooling, metadata and newly generated project art use this repository's MIT license. Legacy-derived motion/procedural geometry retain their documented upstream provenance/terms and are **not** relabeled MIT. No modern upstream VMD, PMD, texture or model binary is redistributed. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).