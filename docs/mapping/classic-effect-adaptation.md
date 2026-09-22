# Classic attack-effect adaptation

This document defines the resource-pack-only visual policy for attack effects on the pinned SlashBlade: Resharped 1.20.1 target (`6e2a0a092fb794d7ea56fd83452869674f3ab1c7`). It is intentionally separate from the VMD motion mapping.

## Why this exists

The classic blade/saya bake changes the weapon path substantially. Resharped's modern slash-effect mesh was authored for its modern animation language, so leaving that mesh unchanged can make the effect arc disagree with the classic-looking weapon motion.

A resource pack cannot replace effect entity logic, but Resharped loads the render meshes/textures through fixed resource locations. We therefore adapt the visual resources while leaving all gameplay/runtime entity behavior authoritative.

## Effect families

| Runtime family | Resharped resource contract | Pack policy | Coverage |
|---|---|---|---|
| `EntitySlashEffect` / `SlashEffectRenderer` | `slashblade:model/util/slash.obj`, `slash.png` | **Classic Interpretation**: generated narrow classic trail adapter | All `AttackManager.doSlash(...)` visuals, including the normal combo families that call it; Void Slash also creates an `EntitySlashEffect` and is covered by the same global override |
| `EntityDrive` / `DriveRenderer` | `slashblade:model/util/drive.obj`, `ss.png` | **Classic Restoration (visual)**: bake the r32 procedural Drive prism into the modern renderer's fixed OBJ coordinate system | Drive-family projectile/wave effect |
| `EntityJudgementCut` / `JudgementCutRenderer` | `slashblade:model/util/slashdim.obj`, `slashdim.png` | **Already classic upstream**: do not duplicate the art in this pack | Judgement Cut dimension effect |

The machine-readable version of this table is `data/effect_resource_contract.json`.

## Global normal-slash adapter

Resharped's `SlashEffectRenderer` has exactly one model/texture pair for every `EntitySlashEffect`. There is no per-combo resource selector. That limitation is useful here: replacing `slash.obj` and `slash.png` once covers every normal slash-effect instance produced through `AttackManager.doSlash`, so A/C/B/air/rapid/rising/Sakura and any other combo using that helper receive the same classic visual language automatically.

The generated `slash.obj` is deliberately a narrow tapered crescent rather than Resharped's large radial disc. `slash.png` is a neutral white/alpha mask with a bright center line and fast head/tail falloff. Resharped can still apply the blade color and rank-dependent render passes because the texture does not bake a fixed hue.

The mesh/texture are new deterministic project assets. They are informed by the *visual language* of r32's `trail.obj`/`trail.png`, but they do not copy those legacy binary art resources.

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
- `SlashEffectRenderer`'s progress rotation (`rotationOffset - 135° * progress`), Y flattening, scale curve and rank passes;
- effect color and critical/rank state;
- Drive entity timing/rotation/alpha curve;
- Judgement Cut seed rotation, echo/wave/wind choreography;
- hitboxes, damage, hit timing, particles, sounds and networking.

Therefore the normal slash replacement is **Classic Interpretation**, not a claim that the old blade-attached `LayerSlashBlade` trail renderer has been restored. If a real-game test shows the classic-shaped ribbon visibly continuing its Java rotation after the weapon has already completed the classic VMD swing, that residual mismatch is `IMPOSSIBLE_RESOURCE_PACK_ONLY` under the first-phase rules.

## Build/validation

`python scripts/build_pack.py` generates the effect resources together with the VMD/PMD output. CI verifies:

- the exact hard-coded runtime paths are present in the ZIP;
- the slash mesh has one `base` ribbon group and a tapered/non-disc geometry;
- the trail texture has transparent ends and a bright center;
- the Drive mesh reconstructs the documented r32 prism under the modern fixed transform;
- Judgement Cut remains deliberately unbundled because its installed Resharped model/texture are already byte-identical at the Git-blob level to r32;
- no Java/Mixin/script/datapack runtime component is introduced.

Runtime visual acceptance is still a real-game check rather than something CI can certify.
