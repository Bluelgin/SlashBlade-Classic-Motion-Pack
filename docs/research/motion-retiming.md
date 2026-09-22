# Motion retiming

There is no old VMD range X–Y to shift. The input is r32's procedural swing function. The offline sampler evaluates it in a normalized legacy swing domain and writes poses into the extracted modern frame windows.

1. Ordinary attack movement uses the conventional six-tick / nine-frame swing baseline. The renderer multiplies normalized progress by 1.2, then applies its original quadratic ease-out. Do not mistake comboResetTicks for swing length.
2. Preserve the slash duration; hold the terminal pose for longer modern follow-through windows. Do not linearly stretch every attack to consume 100+ frames.
3. Recovery begins at source-extracted state/sheath boundaries when a compatible boundary exists. Saya recovery uses a quaternion/translation bridge to neutral; drawn-blade recovery bridges to sampled old Noutou. These connections are explicitly **approximations**. Short aerial recovery windows compress the bridge/recovery, not the main slash.
4. Dense per-frame poses avoid relying on Bezier support that modern NyMmd does not implement. Quaternions remain unit length; all source matrix multiplication order and translations are retained.
5. Shared windows are authored once. It is impossible to give B2/B3 distinct poses at the same resource/frame/bone address. No duplicate keys or nondeterministic merge precedence is permitted in the generic remapper.

## A3 / Sakura-right Battou boundary

The first PoC held the classic `Battou` terminal pose until frame 281 because that is where Resharped enters its final A3/Sakura recovery segment. That was internally valid but too late for the old state cadence.

Official r32 gives `Battou` a `comboResetTicks` value of 12. This is **not** the visible swing duration: the actual weapon swing still uses the short vanilla-swing-derived curve described above. It is, however, the old combo-state timeout after which a drawn move falls into `Noutou`. At the VMD playback rate used here, 12 game ticks correspond to 18 VMD frames. Starting from frame 200 gives frame **218**.

That value is not an arbitrary retime. In pinned Resharped 1.9.65, frame 218 is simultaneously:

- the end of `combo_a3` and start of `combo_a3_end`;
- the end of `sakura_end_right` and start of `sakura_end_finish`.

The shared 200–314 atlas region therefore now holds the short classic Battou swing, keeps its terminal pose through the remainder of the old 12-tick window, and begins the Noutou-style recovery at frame 218. This also avoids inventing a different transition for Sakura End Right, which consumes the same resource/frame addresses.

This build preserves the blade motion formula, not exact hit-synchronized timing across modern mechanics. A4 and A5 hold the source start pose for 8 and 18 frames respectively, placing the slash near the Java impact callbacks; powered A4 uses two source motions. This is adapted anticipation, not recovered old timing. Judgement's five-frame slash slot is an explicit exception to the nine-frame swing. Early combo cancellation and B repeats can jump between poses. These are release-blocking runtime review points, not claimed successes. Timing markers must be compared with recordings before promoting this candidate.

The generic `python -m tools.vmd remap` supports offset and collision-free linear frame scaling while retaining pose and interpolation bytes. It refuses implicit boundary cuts and nonbone tracks to avoid silently corrupting animation. Future authored clip retiming can add piecewise markers with verified Bezier subdivision; it is not falsely claimed implemented here.
