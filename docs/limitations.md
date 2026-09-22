# Limitations and release gates

**Runtime verification pending.** The ZIP is installable by structure; visual acceptance has not passed. This is an experimental candidate, not a complete first-stage restoration.

## Visual limitations

- The official r32 source has procedural blade/saya motion, not a full-body VMD. Player motion is a generated passthrough PMD + neutral VMD adapter. It retains 1.20.1 vanilla poses and cannot claim exact 1.12.2 arms/torso/legs. The user-requested old A1 player clip retimed to 1–41 is therefore **not** implemented as a skeletal clip.
- Exact hand-to-hilt contact and blade/body collision are unverified. The old blade layer itself was independently animated, not a hand-constrained skeleton.
- Modern model scale and geometry are retained. Default model scale differs by about 9.65% from the old final scale. Custom blade offsets, first-person rendering and special models need review.
- Recovery bridges are adapted; early input, shared windows and air/ground transitions can produce discontinuities. No claim that A1–A5 is already visually seamless.
- B/C/Circle/Void/Sakura and modern powered A4/A5 are approximations. Broad slot coverage is not equivalent to faithful restoration.
- Piercing blade data remains upstream. The player PMD adapter changes its body path too.
- No old motion blur geometry, render-target visibility switches or Java-controlled effects are recreated.
- Restart after enabling/disabling the pack is needed because the PMD is statically cached. Simple live enable/disable is not proven sufficient.

## Gameplay limitations

Visual animation adapted; gameplay movement still follows SlashBlade: Resharped. The resource pack cannot edit damage, hitboxes, attack ticks, combo branches, velocity, hit stop, cancellation, invulnerability, targeting, input conditions or Java callbacks. A4/A5 Java body rotations remain. Movement portions of Rapid Slash/Rising Star/Aerial Cleave and similar moves are IMPOSSIBLE_RESOURCE_PACK_ONLY.

## Mapping limitations

Hardcoded frame windows are respected by adapting data. Shared windows cannot represent different animations for different callers. Static player-animation instances and adapter behavior are upstream code. No compatibility mod, mixin, datapack or runtime script is supplied.

## Provenance limitations

The genuine official r32 release and corresponding versioned branch are identified. The JAR download was unavailable, so direct JAR/source equivalence is pending. Legacy custom terms are retained; no upstream binary art is redistributed or relicensed MIT.

## Promotion gates

- Compare r32 and target build in the same viewpoints, with ordinary and powered chains.
- Verify body/weapon alignment, camera behavior, multiplayer and resource activation.
- Tune source-derived timing and recovery within fixed slots.
- Decide whether the vanilla-pose approximation meets the requested visual goal; it must not be presented as recovered skeletal animation.
- Only then publish a stable Release and mark runtime milestones passed.
