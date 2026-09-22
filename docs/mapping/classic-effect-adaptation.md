# Attack-effect adaptation

This document defines the resource-pack-only visual policy for attack effects on the pinned SlashBlade: Resharped 1.20.1 target (`6e2a0a092fb794d7ea56fd83452869674f3ab1c7`). It is intentionally separate from the VMD motion mapping.

## Why the normal slash light is suppressed

The classic blade/saya bake changes the weapon path substantially. Resharped's modern `EntitySlashEffect` is a separately animated effect entity: Java owns its lifetime, progress rotation, flattening, scale, rank passes and color. r32's classic trail was instead attached to the blade renderer and followed the actual blade motion.

A first resource-only attempt replaced Resharped's radial slash mesh with a narrow classic-style ribbon. Runtime testing showed that the result still looked wrong because the modern effect entity continued its own Java rotation independently of the restored blade motion. That mismatch cannot be solved faithfully with an OBJ/PNG replacement alone.

The default pack therefore makes the deliberate choice to show **no normal slash light at all**. This is preferable to shipping a fake classic trail that visibly disagrees with the restored animation.

## Effect families

| Runtime family | Resharped resource contract | Pack policy | Coverage |
|---|---|---|---|
| `EntitySlashEffect` / `SlashEffectRenderer` | `slashblade:model/util/slash.obj`, `slash.png` | **Visual suppression**: microscopic valid mesh + fully transparent texture | All `AttackManager.doSlash(...)` visuals; Void Slash also creates an `EntitySlashEffect` and its slash-light visual is suppressed by the same override |
| `EntityDrive` / `DriveRenderer` | `slashblade:model/util/drive.obj`, `ss.png` | **Classic Restoration (visual)**: bake the r32 procedural Drive prism into the modern renderer's fixed OBJ coordinate system | Drive-family projectile/wave effect |
| `EntityJudgementCut` / `JudgementCutRenderer` | `slashblade:model/util/slashdim.obj`, `slashdim.png` | **Already classic upstream**: do not duplicate the art in this pack | Judgement Cut dimension effect |

The machine-readable version of this table is `data/effect_resource_contract.json`.

## Normal slash-light suppression

Simply deleting `slash.obj/png` from this pack would cause Minecraft to fall back to Resharped's original modern slash light, so the files must remain as overrides.

`scripts/generate_effects.py` therefore generates:

- a tiny, non-degenerate four-vertex `base` quad for `slash.obj`; and
- a fully transparent 1x1 RGBA texture for `slash.png`.

The mesh is kept valid and non-degenerate to avoid OBJ parser/normal edge cases. Its microscopic size is a second safety layer in addition to the transparent texture.

This changes only the **rendered slash-light visual**. The `EntitySlashEffect` entity still exists and Resharped remains authoritative for gameplay, timing, networking, sounds and any non-model behavior attached to it.

## Drive

r32 `RenderDrive.java` did not use an OBJ: it declared a 14-point prism and 12 quads directly in Java, then compressed local X by 0.25. Resharped's `DriveRenderer` instead expects `model/util/drive.obj`, applies a uniform 0.015 scale and a +90 degree Y rotation.

`scripts/generate_effects.py` takes the documented r32 procedural points and pre-transforms them so the fixed Resharped transform reconstructs the classic prism silhouette. `ss.png` is generated as a neutral luminous mask so the modern entity color remains authoritative.

This restores the classic *geometry language*, not the old renderer's exact OpenGL state or alpha function.

## Judgement Cut

No visual replacement is needed for the model/texture contract. The Resharped resource inventory and r32 resource inventory have identical Git blob IDs for both files:

- `slashdim.obj`: `9ab8de31a33970b884df9f4683ece271e9f12889`
- `slashdim.png`: `b79daa73dd545d0a8c3c41c845b083055bd7481a`

Resharped's Java rendering choreography is not identical to r32, but shipping another copy of the same art would not make it more classic and would unnecessarily redistribute upstream art. The installed Resharped copy is therefore left untouched.

## Resource-pack ceiling

The following remain Java-owned and cannot be changed by this phase:

- when an effect entity is spawned;
- effect lifetime and despawn timing;
- `SlashEffectRenderer` progress rotation, flattening, scale curve and rank passes;
- effect color and critical/rank state;
- Drive entity timing/rotation/alpha curve;
- Judgement Cut seed rotation, echo/wave/wind choreography;
- hitboxes, damage, hit timing, particles, sounds and networking.

Because the old blade-attached trail renderer cannot be reconstructed inside Resharped's fixed `EntitySlashEffect` contract, **suppression is the final default policy for normal slash light in the resource-pack-only build**.

## Build/validation

`python scripts/build_pack.py` generates the effect resources together with the VMD/PMD output. CI verifies:

- the hard-coded `slash.obj/png` paths are present so Resharped cannot fall back to its modern slash light;
- `slash.png` is a fully transparent 1x1 RGBA texture;
- `slash.obj` is a microscopic valid `base` quad rather than a visible effect mesh;
- the Drive mesh reconstructs the documented r32 prism under the modern fixed transform;
- Judgement Cut remains deliberately unbundled because its installed Resharped model/texture are already byte-identical to r32;
- no Java/Mixin/script/datapack runtime component is introduced.

Runtime visual acceptance is still a real-game check rather than something CI can certify.
