# In-game acceptance checklist

**Runtime verification pending — no Minecraft GUI was run.** Every item below is NOT RUN.

Record exact Resharped JAR version/hash, Forge version, dependency versions, pack SHA256, skin type, blade model, shader/other animation mods, camera and server/client versions. Start with a clean Minecraft 1.20.1 profile, enable the ZIP at highest priority, then restart the client. Repeat after disabling with a restart for the control comparison. Use official 1.12.2 r32 for legacy comparison footage.

| Move | Status | Evidence / notes |
|---|---|---|
| A1 (Saya1) | NOT RUN | |
| A2 (Saya2) | NOT RUN | |
| A3 | NOT RUN | |
| A4 normal | NOT RUN | verify delayed Noutou final-pose hold after the six-tick swing |
| A4 EX → A5 powered | NOT RUN | verify delayed Noutou final-pose hold after timeout |
| B1–B7 | NOT RUN | |
| C | NOT RUN | |
| Circle Slash | NOT RUN | |
| Aerial Rave A1/A2/A3 | NOT RUN | |
| Aerial B3/B4 | NOT RUN | |
| Aerial Cleave / loop / landing | NOT RUN | |
| Upper Slash / jump | NOT RUN | |
| Rapid Slash / quick | NOT RUN | |
| Rising Star | NOT RUN | |
| Judgement Cut / air / just / end | NOT RUN | installed `slashdim` art is already r32-identical; judge Java choreography separately |
| Void Slash | NOT RUN | SlashDim begins at modern tick 16 / VMD frame 2224; its long-lived `EntitySlashEffect` is also hidden by the global no-slash-light resource policy |
| Sakura End ground/air/finish | NOT RUN | |
| Drive horizontal/vertical | NOT RUN | verify installed Resharped Phantom Blade projectile art is unchanged by this pack |
| Wave Edge | NOT RUN | verify installed Resharped projectile art is unchanged by this pack |
| Guard recovery | NOT RUN | |
| Idle / draw / sheath | NOT RUN | |
| Piercing / Piercing Just | NOT RUN | generated Stinger interpretation + delayed Noutou hold + passthrough player VMD; verify modern lunge alignment |

For every move:

- [ ] Third-person front, back and side: body, blade and sheath alignment.
- [ ] First-person attack motion remains visible; no invisible/misplaced blade, catastrophic clipping or camera intrusion.
- [ ] Do **not** fail phase one solely because the idle/hold camera-relative placement differs from r32. The pinned Resharped renderer hard-codes that outer transform after resetting the incoming pose; exact r32 first-person hold placement is `IMPOSSIBLE_RESOURCE_PACK_ONLY` and is documented in `docs/research/first-person-rendering.md`.
- [ ] Blade does not unexpectedly cross the body; saya follows intended scabbard strikes.
- [ ] Start/end poses have no unwanted teleport, snap or unintended intermediate frame.
- [ ] Slow, normal and earliest possible combo inputs; record discontinuities rather than hiding them.
- [ ] Sheathe/draw and timeout transitions are natural; compare holding versus continuing. For non-saya r32 timeout paths, verify that Noutou reaches its final pose after the six-tick swing and holds briefly before returning to neutral instead of snapping neutral immediately.
- [ ] Walk, run, crouch, jump, land, turn and both skin types.
- [ ] Other client sees remote-player animation; pack installed on observing client.
- [ ] Existing server gameplay, projectile timing and damage remain unchanged.
- [ ] Compare audio separately from motion. Resharped keeps Java-selected modern SoundEvents/pitch/timing; a normal resource pack cannot restore those calls independently without globally replacing vanilla sound assets.
- [ ] Test enable-after-start and restart behavior; record the cache limitation.
- [ ] Capture modern control / candidate / r32 clips at the same playback speed.

## First-person pass

The first-person runtime check has two different goals and must not mix them:

- **Shared motion acceptance:** verify the classic VMD-driven blade/saya motion reads correctly from the camera during A1–A5, air moves, Rapid/Rising, Judgement, Void, Piercing and sheath recovery. This is part of the phase-one candidate.
- **Renderer-wrapper comparison:** record the visual difference between r32's `FPVOldStryleLike` camera-relative hold and Resharped's hard-coded wrapper. This is evidence for the documented ceiling, not a tuning request for `models/item/slashblade.json`.

Specific checks:

- [ ] At idle, document the modern-vs-r32 hold-position difference without treating it as a pack regression.
- [ ] During A1/A2 saya strikes, both blade and sheath remain visible enough to read the scabbard motion.
- [ ] During draw/sheath moves, the weapon does not pass through the camera plane or vanish for an extended interval.
- [ ] Test looking sharply up/down. Resharped uses its own pitch handling; note any uncomfortable camera-relative drift separately from VMD motion errors.
- [ ] Test Projectile Barrier. Do not expect r32's special first-person branch: that branch is Java-only and `IMPOSSIBLE_RESOURCE_PACK_ONLY` in phase one.
- [ ] Do not introduce a global model/PMD/VMD offset merely to improve FPV if it worsens third-person weapon placement.

## Void Slash pass

Void Slash had a source/modern timing mismatch in an earlier candidate: the SlashDim bake began at frame 2200 even though Resharped does not call `doVoidSlashAttack` until elapsed tick 16. The current candidate delays the visual attack to the matching frame offset.

- [ ] Frames 2200–2223 read as preparation/hold, not as a completed early SlashDim strike.
- [ ] At elapsed tick 16 / VMD frame 2224, the SlashDim gesture begins at the same moment Resharped starts the Void Slash release/body-rotation phase.
- [ ] SlashDim resets to neutral at frame 2236; the later long-lived Java effect may continue moving/rotating independently and must be judged as a resource-pack ceiling.
- [ ] At frame 2278, the dedicated modern sheath state starts a fresh Noutou gesture.
- [ ] Noutou reaches its final swing pose at frame 2287, holds it through frame 2292, and returns to neutral at frame 2293.
- [ ] Listen for the modern Void/quick-sheath sounds separately; Java sound timing is not source-restored by this pack.

## Piercing pass

Piercing is a dedicated resource-only Classic Interpretation rather than an upstream fallback. Its binary timing is source-checked; runtime alignment is still visual work:

- [ ] Frames 1–32 read as a stable classic neutral preparation rather than a broken/frozen modern clip.
- [ ] At the modern lunge start (frame 33), the blade snaps into the r32 `Stinger` full-thrust pose at the same moment the Java movement begins.
- [ ] During the first three lunge ticks, the Stinger blade direction agrees with player travel instead of appearing sideways/backwards.
- [ ] `piercing_just` beginning at frame 34 still reads correctly when entering one frame after the main active-state boundary.
- [ ] At frame 63, the old 20-tick Stinger reset clock begins `Noutou`; the transition is not an obvious teleport.
- [ ] The modern quick-sheath sound at frame 65 lands plausibly during the generated Noutou gesture.
- [ ] At frame 72, the six-tick Noutou swing has reached its final pose but **must not** have snapped neutral yet.
- [ ] Frames 72–77 hold the final Noutou pose, reproducing the old `LastActionTime = currentTime + 5` delayed state lifetime.
- [ ] At frame 78 the blade/saya return to the r32 neutral pose and remain stable through frame 90.
- [ ] The generated `piercing_pl.vmd` passthrough leaves the body readable during the Java lunge; no modern full-body Piercing pose should reappear from another pack with higher priority.
- [ ] Do not attribute forward distance, area hit, just-window timing or cancel behavior to this pack. Those remain Resharped Java.

## Slash-light / SA effect pass

For every attack or SA that emits `EntitySlashEffect` (ground/air combo slash effects, Circle Slash, Sakura End, Void Slash and addon consumers):

- [ ] No visible `slash.obj/png` blade light is rendered.
- [ ] Gameplay, damage, sound and entity lifetime still behave normally even though the mesh is invisible.
- [ ] Record any SA that depended on the shared `EntitySlashEffect` art; a resource pack cannot selectively restore it while hiding ordinary slash lights.

For Drive/Wave effects:

- [ ] 幻影刃 and 幻影刃-纵 use the installed Resharped `drive.obj/ss.png` appearance with no pack-induced deformation.
- [ ] 波刀龙胆 likewise keeps the installed projectile art.
- [ ] Third-party `EntityDrive` users are not changed by this pack.

For Judgement Cut:

- [ ] Model/texture appearance remains unchanged from the installed Resharped baseline (the files are already r32-identical).
- [ ] Any difference from r32 is attributed to modern seed/echo/wave/wind Java choreography unless evidence shows an asset issue.

Release gate: observed visual differences, frame/effect-alignment evidence and review of the passthrough-player/fixed-first-person-wrapper/resource-only compromises are required before calling A1 PoC or A1–A5 runtime-complete. Static VMD/ZIP validation alone cannot check these boxes.
