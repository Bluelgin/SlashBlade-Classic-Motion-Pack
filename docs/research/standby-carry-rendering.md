# Standby and back-carry rendering audit

This audit separates two visually similar states that are controlled by different systems in Resharped: the **active main-hand standby pose** and the **back/offhand carry pose**.

## Pinned sources

Legacy r32:

- `flammpfeil/SlashBlade@ba1ef8604c0971f68336b882b42a868df7f32f0b`
- `LayerSlashBlade.java`

Target:

- `0999312/SlashBlade_Resharped@6e2a0a092fb794d7ea56fd83452869674f3ab1c7`
- `LayerMainBlade.java`
- `ISlashBladeState.java`

Normalized source constants live in `data/standby_carry_contract.json`.

## Active main-hand standby is already under VMD control

Resharped `NONE` and `STANDBY` both consume frames `0..1` of `slashblade:combostate/motion.vmd`. The generator fills those frames with `pose(None, 0)` for `hardpointA` and `hardpointB`.

That `None` pose is **not a zero/identity weapon pose**. `tools/vmd/legacy.py` still applies the r32 active-layer base placement before retargeting into the modern hardpoint rig:

```text
translate(0.25, 0.40, -0.50)
scale(0.075)
rotate X +60 deg
rotate Z -20 deg
rotate Y +90 deg
```

The dynamic combo transform is identity for `None`, so frames 0 and 1 encode the old active-layer base placement for both blade and sheath. This means the resource pack already controls and classicizes the main-hand idle/standby weapon pose through the same VMD as attacks.

This should not be confused with the first-person camera wrapper. In first person the VMD standby pose is still evaluated, but it is wrapped inside Resharped's hard-coded first-person matrix described in `first-person-rendering.md`.

## Back/offhand carry is a different renderer path

r32 `renderBack(...)` chooses a `StandbyRenderType` and applies Java transforms for DEFAULT, PSO2 and NINJA carry styles. The first four old ordinal values line up with modern `CarryType` values:

```text
0 NONE
1 DEFAULT
2 PSO2
3 NINJA
```

Resharped extends that enum with `KATANA` and `RNINJA`, serializes it through the same `StandbyRenderType` NBT key, and renders carried blades in `LayerMainBlade.renderStandbyBlade()` using hard-coded Java transforms.

That carry path does **not** consume `combostate/motion.vmd`. Therefore a normal resource pack cannot independently replace the DEFAULT/PSO2/NINJA back-carry matrices with their r32 values.

## Why a model offset is not accepted as a workaround

A resource pack could globally alter a blade model, but that transform would affect active attacks, first person, GUI/fixed contexts or custom blade compatibility as well. It also would not solve multiple carry styles independently. This project therefore does not use model geometry as a hidden carry-pose patch.

Per-blade `adjustXYZ`/carry type is runtime blade state, not a resource-pack selector. The phase-one pack intentionally leaves it authoritative to Resharped.

## Classification

| Visual area | Phase-one result |
|---|---|
| Main-hand `NONE` / `STANDBY` weapon pose | `SUPPORTED_VIA_MOTION_VMD` |
| DEFAULT back carry | `IMPOSSIBLE_RESOURCE_PACK_ONLY` |
| PSO2 back carry | `IMPOSSIBLE_RESOURCE_PACK_ONLY` |
| NINJA back carry | `IMPOSSIBLE_RESOURCE_PACK_ONLY` |
| KATANA / RNINJA carry | Modern target-only runtime behavior |
| Per-blade `adjustXYZ` | Runtime state, not resource-pack controlled |

Runtime testing still needs to confirm that the baked frame-0 classic main-hand pose looks correct with representative blade models, but its implementation path is complete. The separate back-carry difference is a hard resource-pack boundary rather than missing VMD work.
