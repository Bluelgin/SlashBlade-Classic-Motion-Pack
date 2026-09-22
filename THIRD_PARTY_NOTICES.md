# Third-party provenance and terms

## Legacy procedural motion reference

- Author/project: Furia / flammpfeil, SlashBlade.
- Minecraft: 1.12.2; project version: `mc1.12-r32`.
- Branch/commit: `1.12.2`, `ba1ef8604c0971f68336b882b42a868df7f32f0b`.
- Official published file: [SlashBlade-mc1.12-r32.jar, CurseForge 2882699](https://www.curseforge.com/minecraft/mc-mods/slashblade/files/2882699), uploaded by flammpfeil, 2020-02-16.
- Referenced files: `item/ItemSlashBlade.java` (ComboSequence and transitions), `client/renderer/entity/layers/LayerSlashBlade.java` (progress function, transformation order, blade/saya drawing), under `src/main/java/mods/flammpfeil/slashblade/`.
- Shipped derivatives: `tools/vmd/legacy.py`, `data/legacy_motion_map.json`, generated `assets/slashblade/combostate/motion.vmd`. These contain an offline adaptation of the procedural motion; they are not copied old binary assets.

The pinned branch's [src/main/resources/readme.txt](https://github.com/flammpfeil/SlashBlade/blob/ba1ef8604c0971f68336b882b42a868df7f32f0b/src/main/resources/readme.txt) provides a custom use condition:

> 自己責任の下にるなりやくなり好きにするべし。
> 私は責任はとらぬ。

This is a broad permission to use/adapt at one's own responsibility, with no liability assumed by the author. We rely on that project-distributed condition for the procedural adaptation, retain attribution, and do **not** substitute MIT for it. The readme's version heading is stale (1.8.9); the build configuration, branch and official file identify 1.12.2/r32. The source has no blanket MIT license for its art. No legacy texture, model or VMD binary is shipped. The official JAR was identified but its binary could not be downloaded in this environment, so JAR-to-source bytecode equivalence is not asserted.

## Modern contract reference — no art redistribution

- Project: [0999312/SlashBlade_Resharped](https://github.com/0999312/SlashBlade_Resharped).
- Authors credited upstream: Furia; NyMmd: nyatla; Forge OBJ importer; Resharped code: MMF-Group.
- Commit: `6e2a0a092fb794d7ea56fd83452869674f3ab1c7`; Minecraft 1.20.1; mod 1.9.65.
- `gradle.properties`: **MIT License, Art Resources: All Rights Reserved.**
- Inspected files: `model/pa/player_motion.vmd` inventory, `combostate/motion.vmd` inventory, `model/bladeholder.pmd` bone hierarchy, player adapter, blade renderer, NyMmd interpolation, default resources and combo registry.
- Redistribution status: upstream art is **not** included. The pack uses the existing installed bladeholder and game blade models. Its `model/pa/alex.pmd` is a new bone-only format adapter, not a modified copy of upstream Alex. Its player VMD contains newly generated neutral adapter keys, not upstream animation.

## Our license boundary

The existing root MIT license applies to original tooling, tests, documentation, metadata and geometric icon. It does not change the terms of upstream references or the legacy-derived motion noted above. No upstream asset is claimed as our original art. This notice is included in the runtime ZIP.
