# Old Dream Reforged as a validation oracle

Reference project: [`rianfalltwilight-lab/seac-slashblade-old-dream-reforged`](https://github.com/rianfalltwilight-lab/seac-slashblade-old-dream-reforged), pinned at commit `a6b8cf5e3b5b3f270212a47b8d373a95f6a31af3`.

This project is **not** used as a runtime dependency and it is **not** the canonical source for this pack. The canonical provenance remains the official SlashBlade 1.12.2/r32 branch at `ba1ef8604c0971f68336b882b42a868df7f32f0b`. Old Dream Reforged is useful because it independently ports the old procedural blade/saya renderer to a modern SlashBlade environment, so it gives us a second implementation to compare against.

## What Old Dream Reforged actually does

Its legacy path is runtime Java, not a VMD conversion:

- `LegacyMove.java` reconstructs the classic move table (`SAYA1`, `SAYA2`, `BATTOU`, `S_SLASH_EDGE`, etc.) with scabbard flags, amplitudes, directions and reset windows.
- `LegacyBladePose.java` translates the old blade/sheath matrix math to JOML and evaluates it from live swing progress.
- `LegacyHeldRenderer.java` renders the blade and sheath from those matrices and also recreates runtime-only features such as afterimages and the legacy trail.
- `LegacyBodyMotionMixin.java` cancels Resharped's `PlayerAnimationOverrider` for legacy mode, preventing the modern player VMD from taking over.
- `LegacyBodyAnimations.java` restarts the vanilla arm swing clock when a legacy combo begins.
- `LegacyBladePoseMixin.java` intercepts Resharped's `LayerMainBlade` and delegates held-blade rendering to the legacy renderer.

That architecture independently confirms the important historical point behind this resource-pack project: classic SlashBlade weapon motion was procedural Java plus vanilla-style body swing, not a hidden 1.12.2 full-body VMD atlas.

## How this repository uses it

`tools/vmd/old_dream_oracle.py` contains a validation-only representation of the overlapping move table, progress curve and procedural blade/saya transform from the pinned Old Dream Reforged source. `scripts/verify_old_dream_oracle.py` compares it with our independently extracted r32 implementation.

The CI gate verifies:

1. Overlapping move metadata matches: scabbard use, amplitude, direction and enum reset ticks.
2. The swing-progress function agrees at boundary, interior and out-of-range samples.
3. Blade and sheath dynamic matrices agree across multiple time samples.

The comparison intentionally excludes final model scale. VMD bone records cannot encode arbitrary bone scale, and Resharped keeps its installed model-scale contract. The purpose of the oracle is to validate **motion math and transform order**, not to pretend the resource pack can reproduce every runtime renderer detail.

## What the oracle does not prove

Passing the oracle does not prove that the generated resource pack is visually perfect in game. Old Dream Reforged can use runtime state that a resource pack cannot access, including partial ticks, live swing state, dynamic afterimages, trail rendering, barrier rotation, first-person hooks, dual-wield state and explicit Mixin interception.

It also does not turn Old Dream Reforged into the authoritative source for r32. The port describes itself as an r87 procedural translation with later names/behavior added where relevant. When the official 1.12.2/r32 source and Old Dream Reforged differ, this project must document the difference and prefer the official r32 source for the 1.20.1 classic pack.

## Current result

For the overlapping classic move set, the two independent implementations agree on the move parameters, progress function and sampled dynamic transform matrices. This gives the baker a much stronger regression baseline than testing only against its own inverse transform.
