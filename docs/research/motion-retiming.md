# Motion retiming

There is no old VMD range X–Y to shift. The input is r32's procedural swing function. The offline sampler evaluates it in a normalized legacy swing domain and writes poses into the extracted modern frame windows.

1. Ordinary attack movement uses the conventional six-tick / nine-frame swing baseline. The renderer multiplies normalized progress by 1.2, then applies its original quadratic ease-out. Do not mistake `comboResetTicks` for visible swing length.
2. Preserve the slash duration; long modern windows hold the relevant terminal/source pose rather than stretching a six-tick slash over 100+ VMD frames.
3. Source-timed recovery follows the pinned r32 `ItemSlashBlade.onUpdate` target, not a generic blend. `Saya1`/`Saya2` and `SlashDim`/`Iai`/`SIai` reset directly to `None`. Other mapped non-saya moves enter `Noutou`, restart the vanilla swing, reach Noutou's final pose after nine VMD frames, hold it for the remainder of the delayed source state, then return to `None`.
4. r32's default transition into `Noutou` stores `LastActionTime = currentTime + 5`. Noutou itself has `comboResetTicks = 5`, so the source-side state lifetime represented by this bake is ten game ticks / fifteen VMD frames after entry. This is separate from the six-tick swing duration.
5. Dense per-frame poses avoid relying on Bezier support that modern NyMmd does not implement. Quaternions remain unit length; all source matrix multiplication order and translations are retained.
6. Shared windows are authored once. It is impossible to give two modern consumers different poses at the same resource/frame/bone address. No duplicate keys or nondeterministic merge precedence is permitted.

## A3 / Sakura-right shared boundary

The earliest PoC used classic `Battou` in the shared A3 window and held that pose too long. Later source review showed that the powered classic route is better represented by the r32 S-rank language:

`Saya1 → Saya2 → SIai → SSlashEdge → SReturnEdge → SSlashBlade`

The current shared A3 region therefore uses **`SIai`**, not Battou. SIai has `comboResetTicks = 12`; at 30 VMD fps / 20 game tps that is 18 frames. Starting from frame 200 lands at frame **218**.

That frame is also a real pinned Resharped boundary:

- `combo_a3` ends and `combo_a3_end` begins at 218;
- `sakura_end_right` ends and `sakura_end_finish` begins at 218.

Because SIai belongs to r32's direct-to-`None` timeout family, frame 218 becomes neutral. It does **not** enter Noutou. This is especially important because the same VMD addresses also serve Sakura End Right; the pack cannot make that shared region branch dynamically by old Stylish Rank or modern powered state.

## Delayed and compound mappings

Some modern states need an explicit source-clock origin that is not the start of the whole atlas slot.

- A4 EX contains `SSlashEdge` followed by `SReturnEdge`; the final SReturnEdge segment owns the timeout clock.
- Cleave/Sakura-left contains an embedded `Kiriorosi`; that final segment owns the timeout clock.
- Judgement Cut places `SlashDim` at frame 1923, where Resharped enters its slash state, rather than at the start of the preparation state.
- Void Slash is more extreme: Resharped does not call `doVoidSlashAttack` until elapsed tick 16. At 30 VMD fps / 20 game tps the classic SlashDim gesture therefore begins at frame **2224**, not 2200, and its eight-tick r32 reset lands at 2236. The later modern sheath state starts a separate Noutou interpretation at 2278.
- Aerial A1 and Upper jump have modern windows shorter than their corresponding old reset clocks. They are deliberately left as explicit approximations instead of pretending a clamped source timeout is exact.

This build preserves source motion formulas and source timeout semantics where the modern atlas allows it; it does not claim exact hit synchronization across every modern mechanic. A4/A5 anticipation offsets, powered branching, early combo cancellation, B repeats and short aerial windows remain runtime review points.

The generic `python -m tools.vmd remap` supports offset and collision-free linear frame scaling while retaining pose and interpolation bytes. It refuses implicit boundary cuts and nonbone tracks to avoid silently corrupting animation. Future authored clip retiming can add piecewise markers with verified Bezier subdivision; it is not falsely claimed implemented here.
