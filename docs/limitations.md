# Limitations and release gates

**Runtime verification pending.** The ZIP is installable by structure; visual acceptance has not passed. This is an experimental candidate, not a complete first-stage restoration.

## Visual limitations

- The official r32 source has procedural blade/saya motion, not a full-body VMD. Player motion is a generated passthrough PMD + neutral VMD adapter. It retains 1.20.1 vanilla poses and cannot claim exact 1.12.2 arms/torso/legs. The user-requested old A1 player clip retimed to 1–41 is therefore **not** implemented as a skeletal clip.
- Exact hand-to-hilt contact and blade/body collision are unverified. The old blade layer itself was independently animated, not a hand-constrained skeleton.
- Modern model scale and geometry are retained. Default model scale differs by about 9.65% from the old final scale. Custom blade offsets, first-person rendering and special models need review.
- Recovery bridges are adapted; early input, shared windows and air/ground transitions can produce discontinuities. No claim that A1–A5 is already visually seamless.
- B/C/Circle/Void/Sakura and modern powered A4/A5 are approximations. Broad slot coverage is not equivalent to faithful restoration.
- Piercing blade data remains upstream. The player PMD adapter changes its body path too.
- Normal slash-light geometry/texture is now classicized globally through Resharped's fixed `slash.obj/png` resource contract, and Drive gets a baked r32 procedural prism. This does **not** restore r32's blade-attached `LayerSlashBlade` trail renderer: Java still controls effect spawn timing, lifetime, progress rotation, scale/flattening, rank passes and colors. Those differences are `IMPOSSIBLE_RESOURCE_PACK_ONLY` in phase one.
- Judgement Cut's installed Resharped `slashdim.obj/png` files are already identical to the r32 resource blobs, so the pack leaves them untouched. Its modern Java echo/wave/wind choreography remains authoritative.
- Other Java-only render-target visibility switches, dynamic blur-copy count and GL-state choreography are not recreated.
- Restart after enabling/disabling the pack is needed because the PMD is statically cached. Simple live enable/disable is not proven sufficient.

## Gameplay limitations

Visual animation/effect assets are adapted; gameplay movement still follows SlashBlade: Resharped. The resource pack cannot edit damage, hitboxes, attack ticks, combo branches, velocity, hit stop, cancellation, invulnerability, targeting, input conditions or Java callbacks. A4/A5 Java body rotations remain. Movement portions of Rapid Slash/Rising Star/Aerial Cleave and similar moves are IMPOSSIBLE_RESOURCE_PACK_ONLY.

## Mapping limitations

Hardcoded frame windows are respected by adapting data. Shared windows cannot represent different animations for different callers. Static player-animation instances and adapter behavior are upstream code. Effect resources are likewise global per renderer: all `EntitySlashEffect` instances share one `slash.obj/png`, so a resource pack cannot choose a different trail mesh per combo. No compatibility mod, mixin, datapack or runtime script is supplied.

## Provenance limitations

The genuine official r32 release and corresponding versioned branch are identified. The JAR download was unavailable, so direct JAR/source equivalence is pending. Legacy custom terms are retained; no upstream binary art is redistributed or relicensed MIT. The classic trail adapter is newly generated project art; procedural Drive coordinates retain their documented legacy-source provenance.

## Promotion gates

- Compare r32 and target build in the same viewpoints, with ordinary and powered chains.
- Verify body/weapon alignment, camera behavior, multiplayer and resource activation.
- Verify classic trail alignment across A/B/C/air/rapid/rising/Sakura/Void flows and confirm the fixed modern `-135° * progress` rotation does not create unacceptable post-swing drift.
- Verify the baked classic Drive prism orientation for both horizontal and vertical/wave usages.
- Tune source-derived timing and recovery within fixed slots.
- Decide whether the vanilla-pose and resource-only effect approximations meet the requested visual goal; they must not be presented as recovered skeletal animation or the old Java trail renderer.
- Only then publish a stable Release and mark runtime milestones passed.
