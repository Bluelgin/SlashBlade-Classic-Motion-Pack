# Limitations and release gates

**Phase-one source/resource implementation is complete; Minecraft runtime verification is pending.** The ZIP is structurally installable and all known resource-pack-controllable subsystems have an implemented path. Visual acceptance has not passed, so this remains a release candidate rather than a verified stable release. See `data/phase_one_scope.json` and `docs/phase-one-status.md`.

## Visual limitations

- The official r32 source has procedural blade/saya motion, not a full-body VMD. Player motion uses a generated missing-bone passthrough PMD/VMD adapter. On the pinned target, missing player bones return the incoming `value0`, suppressing Resharped's custom skeletal SlashBlade clip without inventing a historical skeleton.
- r32 also restarts Minecraft's vanilla swing clock in Java. A resource pack cannot set that runtime swing state for every accepted combo. The passthrough adapter therefore preserves whatever underlying pose exists; it does **not** claim exact r32 arm-swing event timing. A fixed synthetic arm VMD is intentionally not substituted because it would overwrite contextual handedness/walk/head/pose input and would be a new unverified approximation.
- Resharped can apply Java-owned user-pose/root rotations around the weapon layer. Those cannot be removed by the PMD/VMD adapter and remain `IMPOSSIBLE_RESOURCE_PACK_ONLY`.
- Exact hand-to-hilt contact and blade/body collision are unverified. The old blade layer itself was independently animated, not a hand-constrained skeleton.
- Modern model scale and geometry are retained. Default model scale differs by about 9.65% from the old final scale. A universal correction is not safely expressible through the shared VMD for arbitrary custom blades; global geometry edits would affect unrelated contexts/models.
- **Classic first-person idle/hold placement is `IMPOSSIBLE_RESOURCE_PACK_ONLY` on the pinned target.** Resharped's `BladeFirstPersonRender` resets the incoming `PoseStack` pose/normal matrices to identity and then applies a hard-coded first-person matrix before invoking `LayerMainBlade`. Item-model `firstperson_righthand` / `firstperson_lefthand` display transforms therefore cannot replace that matrix. The shared VMD attack motion is still visible in first person, but the outer camera-relative hold position/angle cannot be changed independently without runtime code.
- r32's Projectile Barrier first-person branch, pitch-sync policy and first-person blur controls are also Java runtime behavior and are `IMPOSSIBLE_RESOURCE_PACK_ONLY`. A global model/PMD/VMD offset is not accepted as a workaround because it also changes third-person placement. See `docs/research/first-person-rendering.md`.
- Main-hand `NONE` / `STANDBY` is resource-controlled and already uses the retargeted r32 neutral pose in VMD frames 0..1. By contrast, DEFAULT/PSO2/NINJA back/offhand carry transforms are hard-coded in Resharped `renderStandbyBlade()` and are `IMPOSSIBLE_RESOURCE_PACK_ONLY`. See `docs/research/standby-carry-rendering.md`.
- Recovery timing is source-derived where the old reset clock is known, but early input, shared windows and air/ground transitions can still produce visual discontinuities that require runtime acceptance.
- B/C/Circle/Void/Sakura and modern powered/shared families are explicit Classic Interpretation cases. Broad slot coverage is not equivalent to an exact historical semantic mapping.
- Piercing blade data remains upstream. The player passthrough adapter is global and also affects its body-animation path.
- Normal slash-light geometry/texture is classicized globally through Resharped's fixed `slash.obj/png` resource contract, and Drive gets a baked r32 procedural prism. This does **not** restore r32's blade-attached `LayerSlashBlade` trail/afterimage renderer: Java still controls effect spawn timing, lifetime, progress rotation, scale/flattening, rank passes, colors, dynamic copy count and blur progress. Those differences are `IMPOSSIBLE_RESOURCE_PACK_ONLY` in phase one.
- Judgement Cut's installed Resharped `slashdim.obj/png` files are already identical to the r32 resource blobs, so the pack leaves them untouched. Its modern Java echo/wave/wind choreography remains authoritative.
- Other Java-only render-target visibility switches, Projectile Barrier trail branches and GL-state choreography are not recreated.
- Restart after enabling/disabling the pack is needed because the PMD is statically cached. Simple live enable/disable is not a valid acceptance comparison.

## Gameplay limitations

Visual animation/effect assets are adapted; gameplay movement still follows SlashBlade: Resharped. The resource pack cannot edit damage, hitboxes, attack ticks, combo branches, rank/timing branch selection, velocity, hit stop, cancellation, invulnerability, targeting, input conditions or Java callbacks. Movement portions of Rapid Slash/Rising Star/Aerial Cleave and similar moves remain runtime-owned.

## Mapping limitations

Hardcoded frame windows are respected by adapting data. Shared windows cannot represent different animations for different callers. Static player-animation instances and adapter behavior are upstream code. Effect resources are likewise global per renderer: all `EntitySlashEffect` instances share one `slash.obj/png`, so a resource pack cannot choose a different trail mesh per combo. The first-person camera wrapper and back-carry transforms are separate hard-coded renderer transforms, not VMD slots. No compatibility mod, Mixin, datapack or runtime script is supplied.

## Provenance limitations

The genuine official r32 release and corresponding versioned branch are identified. The JAR download was unavailable in the research environment, so direct JAR/source byte-equivalence remains pending. Legacy custom terms are retained; no upstream binary art is redistributed or relicensed MIT. The classic trail adapter is newly generated project art; procedural Drive coordinates retain their documented legacy-source provenance.

## Promotion gates

The source-complete RC becomes runtime-complete only after the following checks are actually observed in Minecraft:

- Compare official r32, unmodified target and candidate in matched viewpoints/speeds for ordinary and powered chains.
- Verify body/weapon alignment, camera safety, multiplayer/remote players and resource activation/restart behavior.
- Verify A1–A5 plus air/special transition feel at normal and earliest legal combo input timing.
- In first person, verify that the shared classic VMD motion remains visible and usable, with no disappearance, severe clipping or camera intrusion. Do **not** require the r32 static hold matrix itself; that difference is a documented hard ceiling.
- Verify classic trail alignment across A/B/C/air/rapid/rising/Sakura/Void flows and confirm the fixed modern progress rotation does not create unacceptable post-swing drift.
- Verify the baked classic Drive prism orientation for horizontal and vertical/wave usages.
- Test representative custom blade models, crouch/walk/jump/landing and both player skin geometries.
- Decide whether the pose-passthrough, fixed first-person/carry wrappers and resource-only effect approximations meet the visual goal. They must not be presented as recovered skeletal animation, restored r32 FPV Java, old swing-clock Java or the old Java trail renderer.
- Only then publish a verified stable Release and set `runtime_complete` true.
