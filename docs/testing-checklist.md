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
| Judgement Cut / air / just / end | NOT RUN | |
| Void Slash | NOT RUN | |
| Sakura End ground/air/finish | NOT RUN | |
| Drive horizontal/vertical | NOT RUN | |
| Wave Edge | NOT RUN | |
| Guard recovery | NOT RUN | |
| Idle / draw / sheath | NOT RUN | |
| Piercing regression | NOT RUN | |

For every move:

- [ ] Third-person front, back and side: body, blade and sheath alignment.
- [ ] First-person view: no invisible/misplaced blade, camera intrusion or broken arms.
- [ ] Blade does not unexpectedly cross the body; saya follows intended scabbard strikes.
- [ ] Start/end poses have no unwanted teleport, snap or unintended intermediate frame.
- [ ] Slow, normal and earliest possible combo inputs; record discontinuities rather than hiding them.
- [ ] Sheathe/draw and timeout transitions are natural; compare holding versus continuing.
- [ ] Walk, run, crouch, jump, land, turn and both skin types.
- [ ] Other client sees remote-player animation; pack installed on observing client.
- [ ] Existing server gameplay, projectile timing and damage remain unchanged.
- [ ] Test enable-after-start and restart behavior; record the cache limitation.
- [ ] Capture modern control / candidate / r32 clips at the same playback speed.

Release gate: observed visual differences, frame-alignment evidence and review of the passthrough-player compromise are required before calling A1 PoC or A1–A5 runtime-complete. Static VMD/ZIP validation alone cannot check these boxes.
