# Motion retiming

There is no old VMD range X–Y to shift. The input is r32's procedural swing function. The offline sampler evaluates it in a normalized legacy swing domain and writes poses into the extracted modern frame windows.

1. Ordinary attack movement uses the conventional six-tick / nine-frame swing baseline. The renderer multiplies normalized progress by 1.2, then applies its original quadratic ease-out. Do not mistake comboResetTicks for swing length.
2. Preserve the slash duration; hold the terminal pose for longer modern follow-through windows. Do not linearly stretch every attack to consume 100+ frames.
3. Recovery begins at source-extracted modern sheath/recovery boundaries. Saya recovery uses a quaternion/translation bridge to neutral; drawn-blade recovery bridges to sampled old Noutou. These connections are explicitly **approximations**. Short aerial recovery windows compress the bridge/recovery, not the main slash.
4. Dense per-frame poses avoid relying on Bezier support that modern NyMmd does not implement. Quaternions remain unit length; all source matrix multiplication order and translations are retained.
5. Shared windows are authored once. It is impossible to give B2/B3 distinct poses at the same resource/frame/bone address. No duplicate keys or nondeterministic merge precedence is permitted in the generic remapper.

This build preserves the blade motion formula, not exact hit-synchronized timing across modern mechanics. A4 and A5 hold the source start pose for 8 and 18 frames respectively, placing the slash near the Java impact callbacks; powered A4 uses two source motions. This is adapted anticipation, not recovered old timing. Judgement's five-frame slash slot is an explicit exception to the nine-frame swing. Early combo cancellation and B repeats can jump between poses. These are release-blocking runtime review points, not claimed successes. Timing markers must be compared with recordings before promoting this candidate.

The generic `python -m tools.vmd remap` supports offset and collision-free linear frame scaling while retaining pose and interpolation bytes. It refuses implicit boundary cuts and nonbone tracks to avoid silently corrupting animation. Future authored clip retiming can add piecewise markers with verified Bezier subdivision; it is not falsely claimed implemented here.
