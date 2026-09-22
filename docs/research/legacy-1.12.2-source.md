# Official 1.12.2 source and provenance

Research target: official `flammpfeil/SlashBlade`, **1.12.2 branch**, commit `ba1ef8604c0971f68336b882b42a868df7f32f0b`. Master was not used as the old-version reference.

`build.gradle` declares `version = "mc1.12-r32"` and Forge/Minecraft `1.12.2-14.23.5.2847`. The author's published [CurseForge file 2882699](https://www.curseforge.com/minecraft/mc-mods/slashblade/files/2882699) is `SlashBlade-mc1.12-r32.jar`, explicitly supports 1.12.2, and was uploaded by flammpfeil on 2020-02-16. This anchors the branch to a real player-facing version, not an arbitrary old commit. No GitHub release entries were returned. The published JAR download timed out, so exact release bytecode/source identity remains unverified.

## There is no legacy VMD atlas

The complete recursive tree of this pinned branch contains **zero `.vmd`, `.pmd` or `.vmc` files**. It has OBJ models and textures. The key animation source is procedural:

- `ItemSlashBlade.java:214` defines 34 ComboSequence values, amplitude, direction, saya usage and reset ticks. Reset ticks are **not** animation duration.
- `ItemSlashBlade.java`, `getNextComboSeq`: ground right-click chain starts Saya1 → Saya2 → Battou, or SIai → SSlashEdge → SReturnEdge → SSlashBlade depending on rank and timing. Normal left-click alternates Kiriage/Kiriorosi. There is no old enum literally named modern A1.
- `LayerSlashBlade.java:575–605`: swing progress is multiplied by 1.2 and clamped; most moves apply `1-(1-p)^2`; Iai/SIai use a triangular progression; thrusts use a fixed progress.
- `LayerSlashBlade.java:629–809`: base placement, scale and blade transformation chain, with dedicated Kiriorosi and negative-direction branches.
- `LayerSlashBlade.java:984–1010`: corresponding saya transform, active for scabbard strikes.
- `ItemSlashBlade.doSwingItem`: triggers the vanilla swing. `CoreProxyClient.postInit` adds the blade layer to existing living renderers. There is no recovered whole-body skeletal atlas here.

The implementation therefore samples the actual old rendering formula into VMD hardpoint transforms. It does **not** rename a modern or imagined animation as a legacy binary. See `data/legacy_motion_map.json` and `tools/vmd/legacy.py`.

## Limits of the source equivalence claim

The bake models a standing adult, right-hand, default-adjustment player and ordinary swing cadence. Skin meshes, crouching, other mods, first-person camera behavior, haste/fatigue, Java effects, dual-wield logic and gameplay motion are not recreated. Modern weapon geometry and scale remain installed-game assets. Runtime verification pending.

Asset/derivative terms and the stale resource readme version heading are explicitly documented in `THIRD_PARTY_NOTICES.md`.
