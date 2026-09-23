# Limitations and release gates

**Runtime verification pending.** The ZIP is installable by structure; visual acceptance has not passed. This is an experimental candidate, not a complete first-stage restoration.

## Visual limitations

- The official r32 source has procedural blade/saya motion, not a full-body VMD. Player motion is a generated passthrough PMD + neutral VMD adapter. It retains 1.20.1 vanilla poses and cannot claim exact 1.12.2 arms/torso/legs. The user-requested old A1 player clip retimed to 1–41 is therefore **not** implemented as a skeletal clip.
- Exact hand-to-hilt contact and blade/body collision are unverified. The old blade layer itself was independently animated, not a hand-constrained skeleton.
- Modern model scale and geometry are retained. Default model scale differs by about 9.65% from the old final scale. Custom blade offsets and special models need review.
- **Classic first-person idle/hold placement is `IMPOSSIBLE_RESOURCE_PACK_ONLY` on the pinned target.** Resharped's `BladeFirstPersonRender` resets the incoming `PoseStack` pose/normal matrices to identity and then applies a hard-coded first-person matrix before invoking `LayerMainBlade`. Item-model `firstperson_righthand` / `firstperson_lefthand` display transforms therefore cannot replace that matrix. The shared VMD attack motion is still visible in first person, but the outer camera-relative hold position/angle cannot be changed independently without runtime code.
- r32's Projectile Barrier first-person branch, pitch-sync policy and first-person blur controls are also Java runtime behavior and are `IMPOSSIBLE_RESOURCE_PACK_ONLY`. A global model/PMD/VMD offset is not accepted as a workaround because it also changes third-person placement. See `docs/research/first-person-rendering.md`.
- Recovery bridges are adapted; early input, shared windows and air/ground transitions can produce discontinuities. No claim that A1–A5 is already visually seamless.
- Source-timed non-saya timeouts now preserve r32's delayed Noutou state: after the six-tick swing reaches its final pose, that pose is held until the source Noutou clock expires. Modern state boundaries can still cut this hold short in narrow shared atlas windows.
- B/C/Circle/Void/Sakura and modern powered A4/A5 are approximations. Broad slot coverage is not equivalent to faithful restoration.
- Void Slash is a modern Classic Interpretation, not an r32 move-for-move port. Its SlashDim visual is delayed to Resharped's real tick-16 Java release (VMD frame 2224), then resets at frame 2236; the later dedicated sheath state uses Noutou. The long-lived modern Void effect continues under Java control after the weapon gesture ends.
- Piercing no longer falls back to upstream animation assets: the pack now generates both dedicated Piercing VMDs. Its blade path is a modern `CLASSIC_INTERPRETATION` using the r32 Stinger full-thrust pose and source-timed delayed Noutou recovery, while its player VMD is a passthrough adapter. Forward lunge, area hit, just timing, sound timing and cancellation remain modern Java and are not restored to r32 behavior.
- Normal `EntitySlashEffect` blade light is globally suppressed through Resharped's fixed `slash.obj/png` contract. This also hides any SA/addon visual that reuses the same renderer; a resource pack cannot distinguish the caller. `drive.obj/ss.png` are deliberately left untouched after runtime testing showed that overriding them rewrites 幻影刃 / 幻影刃-纵 / 波刀龙胆 projectile art. Java still controls effect timing, rotation, color and gameplay.
- Judgement Cut's installed Resharped `slashdim.obj/png` files are already identical to the r32 resource blobs, so the pack leaves them untouched. Its modern Java echo/wave/wind choreography remains authoritative.
- Other Java-only render-target visibility switches, dynamic blur-copy count and GL-state choreography are not recreated.
- Restart after enabling/disabling the pack is needed because the PMD is statically cached. Simple live enable/disable is not proven sufficient.

## Audio limitations

Classic r32 attack audio is not a self-contained SlashBlade sound bank that can simply be copied into this pack. The pinned r32 code frequently calls vanilla Minecraft SoundEvents with distinctive runtime parameters; for example the normal `doSlashBladeAttack` path uses `ENTITY_PLAYER_ATTACK_SWEEP` at volume `0.8` and pitch `0.01`. Resharped instead chooses modern Java sounds/timing such as `TRIDENT_THROW` for slash effects and Piercing and `CHAIN_HIT` for quick sheath actions.

A normal resource pack can replace the audio files behind a vanilla SoundEvent, but it cannot change which SoundEvent Resharped Java calls, the per-call pitch/volume, or the callback tick. Replacing `minecraft:entity.trident.throw` or chain assets would also change ordinary Minecraft tridents/chains globally. Therefore exact r32 sound-event selection, pitch and timing are **`IMPOSSIBLE_RESOURCE_PACK_ONLY` without global vanilla-audio side effects**. The default pack deliberately does not perform those global replacements.

This also leaves some unavoidable audio/visual differences. A source-timed classic Noutou can begin before Resharped reaches a later modern END state that plays `CHAIN_HIT`; the weapon motion can therefore read as old-style while the sheath sound remains on the modern Java clock. Treat that as a documented runtime ceiling, not as evidence that the VMD timeout itself is wrong.

## Gameplay limitations

Visual animation/effect assets are adapted; gameplay movement still follows SlashBlade: Resharped. The resource pack cannot edit damage, hitboxes, attack ticks, combo branches, velocity, hit stop, cancellation, invulnerability, targeting, input conditions or Java callbacks. A4/A5 Java body rotations remain. Movement portions of Rapid Slash/Rising Star/Aerial Cleave/Piercing and similar moves are `IMPOSSIBLE_RESOURCE_PACK_ONLY`.

## Mapping limitations

Hardcoded frame windows are respected by adapting data. Shared windows cannot represent different animations for different callers. Static player-animation instances and adapter behavior are upstream code. Effect resources are likewise global per renderer: all `EntitySlashEffect` instances share one `slash.obj/png`, so a resource pack cannot choose a different trail mesh per combo. The first-person camera-relative wrapper is another hard-coded renderer transform and is not a VMD slot. Runtime back/offhand `CarryType` placement is also Java-only. No compatibility mod, mixin, datapack or runtime script is supplied.

## Provenance limitations

The genuine official r32 release and corresponding versioned branch are identified. The JAR download was unavailable, so direct JAR/source equivalence is pending. Legacy custom terms are retained; no upstream binary art is redistributed or relicensed MIT. The slash-suppression assets are newly generated project art. No Drive or Judgement Cut projectile/model art is shipped by this pack.

## Promotion gates

- Compare r32 and target build in the same viewpoints, with ordinary and powered chains.
- Verify body/weapon alignment, camera safety, multiplayer and resource activation.
- In first person, verify that the shared classic VMD motion remains visible and usable, with no disappearance, severe clipping or camera intrusion. Do **not** require the r32 static hold matrix itself for phase-one acceptance; that difference is a documented resource-pack ceiling.
- Verify source-timed Noutou recovery: six-tick motion to the final pose, then a short final-pose hold before neutral where the modern atlas window is long enough.
- Verify Piercing's frame-33 Stinger commit, modern forward lunge alignment, frame-63 Noutou recovery, frame-72 final Noutou pose and frame-78 neutral return. Confirm the passthrough player body does not make the lunge unreadable.
- Verify Void Slash remains in preparation through frame 2223, begins SlashDim at the modern tick-16/frame-2224 release, resets at 2236, then plays the separate Noutou sheath stage at 2278–2293.
- Verify that global slash-light suppression is acceptable for Circle Slash, Sakura End, Void Slash and any addon using `EntitySlashEffect`; selective per-caller restoration is not resource-pack-only.
- Verify that 幻影刃, 幻影刃-纵, 波刀龙胆 and third-party `EntityDrive` visuals remain identical to the installed Resharped/addon baseline.
- Compare attack/sheath audio separately and record modern Java-selected SoundEvent/pitch/timing differences rather than misclassifying them as animation regressions.
- Tune source-derived timing and recovery within fixed slots.
- Decide whether the vanilla-pose, fixed first-person-wrapper, modern-audio and resource-only effect approximations meet the requested visual goal; they must not be presented as recovered skeletal animation, restored r32 FPV Java, restored r32 sound orchestration, or the old Java trail renderer.
- Only then publish a stable Release and mark runtime milestones passed.
