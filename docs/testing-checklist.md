# In-game acceptance checklist

**Runtime verification pending — no Minecraft GUI was run.** Every item below is NOT RUN.

Record exact Resharped JAR version/hash, Forge version, dependency versions, pack SHA256, skin type, blade model, shader/other animation mods, camera and server/client versions. Start with a clean Minecraft 1.20.1 profile, enable the ZIP at highest priority, then restart the client. Repeat after disabling with a restart for the control comparison. Use official 1.12.2 r32 for legacy comparison footage.

| Move | Status | Evidence / notes |
|---|---|---|
| A1 (Saya1) | NOT RUN | |
| A2 (Saya2) | NOT RUN | |
| A3 | NOT RUN | |
| A4 normal | NOT RUN | |
| A4 EX → A5 powered | NOT RUN | |
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
| Void Slash | NOT RUN | global classic trail adapter applies to its long-lived `EntitySlashEffect` too |
| Sakura End ground/air/finish | NOT RUN | |
| Drive horizontal/vertical | NOT RUN | verify restored prism orientation and scale |
| Wave Edge | NOT RUN | verify restored prism orientation and scale |
| Guard recovery | NOT RUN | |
| Idle / draw / sheath | NOT RUN | |
| Piercing / Piercing Just | NOT RUN | generated Stinger interpretation + passthrough player VMD; verify modern lunge alignment |

For every move:

- [ ] Third-person front, back and side: body, blade and sheath alignment.
- [ ] First-person attack motion remains visible; no invisible/misplaced blade, catastrophic clipping or camera intrusion.
- [ ] Do **not** fail phase one solely because the idle/hold camera-relative placement differs from r32. The pinned Resharped renderer hard-codes that outer transform after resetting the incoming pose; exact r32 first-person hold placement is `IMPOSSIBLE_RESOURCE_PACK_ONLY` and is documented in `docs/research/first-person-rendering.md`.
- [ ] Blade does not unexpectedly cross the body; saya follows intended scabbard strikes.
- [ ] Start/end poses have no unwanted teleport, snap or unintended intermediate frame.
- [ ] Slow, normal and earliest possible combo inputs; record discontinuities rather than hiding them.
- [ ] Sheathe/draw and timeout transitions are natural; compare holding versus continuing.
- [ ] Walk, run, crouch, jump, land, turn and both skin types.
- [ ] Other client sees remote-player animation; pack installed on observing client.
- [ ] Existing server gameplay, projectile timing and damage remain unchanged.
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

## Piercing pass

Piercing is now a dedicated resource-only Classic Interpretation rather than an upstream fallback. Its binary timing is source-checked; runtime alignment is still visual work:

- [ ] Frames 1–32 read as a stable classic neutral preparation rather than a broken/frozen modern clip.
- [ ] At the modern lunge start (frame 33), the blade snaps into the r32 `Stinger` full-thrust pose at the same moment the Java movement begins.
- [ ] During the first three lunge ticks, the Stinger blade direction agrees with player travel instead of appearing sideways/backwards.
- [ ] `piercing_just` beginning at frame 34 still reads correctly when entering one frame after the main active-state boundary.
- [ ] At frame 63, the old 20-tick Stinger reset clock begins `Noutou`; the transition is not an obvious teleport.
- [ ] The modern quick-sheath sound at frame 65 lands plausibly during the generated Noutou gesture.
- [ ] By frame 72 the blade/saya are back at the r32 neutral pose and remain stable through frame 90.
- [ ] The generated `piercing_pl.vmd` passthrough leaves the body readable during the Java lunge; no modern full-body Piercing pose should reappear from another pack with higher priority.
- [ ] Do not attribute forward distance, area hit, just-window timing or cancel behavior to this pack. Those remain Resharped Java.

## Classic trail / effect pass

For every attack that emits the normal `EntitySlashEffect` (ground A/B/C chains, air chains, Rapid/Rising/Sakura and other `AttackManager.doSlash` callers):

- [ ] The modern broad radial disc is replaced by a narrow, tapered classic-looking afterimage.
- [ ] The trail is on the same visual side of the weapon swing and does not appear mirrored.
- [ ] At the actual hit/swing moment the brightest core is close enough to the classic blade path to read as one motion.
- [ ] On fast multi-hit moves, repeated trail entities do not form an opaque modern-looking wheel.
- [ ] On slow/long-lived Void Slash, record whether Resharped's fixed `rotationOffset - 135° * progress` causes the ribbon to rotate after the classic weapon motion has ended. If so, mark the residual as `IMPOSSIBLE_RESOURCE_PACK_ONLY`, not as an OBJ bug.
- [ ] Low and high Concentration Rank: Java's black/color/white layered passes still remain readable with the neutral classic alpha mask.
- [ ] Different blade colors tint the trail cleanly; no color is baked into the replacement texture.

For Drive/Wave effects:

- [ ] Horizontal Drive has the old compact prism/bolt silhouette, not an oversized plane.
- [ ] Vertical Drive and Wave Edge are not rotated 90° off-axis by the old→modern pre-transform.
- [ ] Alpha/color remain controlled by Resharped and fade without texture seams.

For Judgement Cut:

- [ ] Model/texture appearance remains unchanged from the installed Resharped baseline (the files are already r32-identical).
- [ ] Any difference from r32 is attributed to modern seed/echo/wave/wind Java choreography unless evidence shows an asset issue.

Release gate: observed visual differences, frame/effect-alignment evidence and review of the passthrough-player/fixed-first-person-wrapper/resource-only compromises are required before calling A1 PoC or A1–A5 runtime-complete. Static VMD/ZIP validation alone cannot check these boxes.