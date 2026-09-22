# First-person rendering audit

This note records the resource-pack ceiling for the classic first-person holding view. It is deliberately separate from the blade/saya VMD bake because the two systems live at different points in the render pipeline.

## Pinned sources

Legacy reference:

- `flammpfeil/SlashBlade`
- official `1.12.2` branch
- commit `ba1ef8604c0971f68336b882b42a868df7f32f0b`
- `src/main/java/mods/flammpfeil/slashblade/client/renderer/entity/BladeFirstPersonRender.java`

Target:

- `0999312/SlashBlade_Resharped`
- commit `6e2a0a092fb794d7ea56fd83452869674f3ab1c7`
- `src/main/java/mods/flammpfeil/slashblade/client/renderer/SlashBladeTEISR.java`
- `src/main/java/mods/flammpfeil/slashblade/client/renderer/model/BladeFirstPersonRender.java`
- `src/main/java/mods/flammpfeil/slashblade/client/renderer/layers/LayerMainBlade.java`

The normalized operation lists are also pinned in `data/first_person_render_contract.json`.

## What r32 actually does

The r32 first-person renderer is Java-driven. With `FPVOldStryleLike` enabled and Projectile Barrier inactive, it applies the following camera-relative transform before asking `LayerSlashBlade` to render the classic procedural blade/sheath layer:

```text
sync player pitch
translate(-0.35, -0.10, -0.80)
rotate -3 deg around +X
rotate 180 deg around +Z
translate(0, +0.25, 0)
rotate -25 deg around approximately (0.9, 0.1, 0)
scale(1.2, 1.0, 1.0)
```

Projectile Barrier uses a separate first-person branch: its first translation becomes `(0, +0.1, -0.8)` and the first X rotation becomes `-30 deg`. r32 also controls pitch synchronization and first-person blur behavior in Java.

The important architectural point is that these values are **not item-model display JSON**. They belong to the old runtime renderer.

## What Resharped 1.9.65 does

`SlashBladeTEISR` routes first-person SlashBlade rendering to the modern `BladeFirstPersonRender`. That renderer immediately resets the current `PoseStack` pose and normal matrices to identity, then applies its own fixed transform:

```text
identity
translate(0, 0, -0.5)
rotate +180 deg around Z
scale(1.2, 1.0, 1.0)
rotate X by -player pitch
```

It then invokes `LayerMainBlade`, which evaluates the same `combostate/motion.vmd` hardpoint motion used by the normal blade layer.

The identity reset is the decisive constraint. A resource pack can replace `assets/slashblade/models/item/slashblade.json`, but a `firstperson_righthand`/`firstperson_lefthand` display transform cannot replace the SlashBlade camera-relative hold transform on this pinned target: any incoming transform that reached the custom item renderer has been discarded before the blade layer is drawn.

## What the resource pack can still change

The classic blade and sheath motion itself remains visible in first person because `LayerMainBlade` still consumes the pack's VMD. Therefore attack arcs, saya strikes, draw/sheath hardpoint motion and the generated attack-effect assets remain part of the first-person result.

What cannot be independently changed is the outer camera-relative first-person placement that wraps that shared motion. A global offset baked into the blade model, PMD or VMD would affect third-person rendering too. It is not a valid first-person-only fix.

| First-person feature | Phase-one resource pack |
|---|---|
| Classic blade/saya attack motion | `SUPPORTED` through shared VMD |
| Classic static hold position/angle | `IMPOSSIBLE_RESOURCE_PACK_ONLY` |
| r32 Projectile Barrier FPV branch | `IMPOSSIBLE_RESOURCE_PACK_ONLY` |
| r32 pitch-sync policy | `IMPOSSIBLE_RESOURCE_PACK_ONLY` |
| Item-model `firstperson_*` display override | `INEFFECTIVE_ON_PINNED_TARGET` |
| Global model/VMD offset | Rejected: would regress third person |

## Consequence for phase one

Do **not** add a `models/item/slashblade.json` override and claim the old first-person hold was restored. That would be structurally present but would not control the actual pinned Resharped first-person renderer.

The release acceptance target is therefore:

1. classic attack motion remains coherent and visible from first person;
2. no blade disappearance, clipping catastrophe or camera intrusion is introduced by the VMD bake;
3. the camera-relative idle/hold difference from r32 is documented as `IMPOSSIBLE_RESOURCE_PACK_ONLY`;
4. a future runtime companion, if the project ever permits one, would be the correct layer for an exact port of the old first-person transform and Projectile Barrier branch.

This is a hard implementation boundary for the current project constraint, not an unfinished JSON-tuning task.
