# Resharped loading contract

Pinned master: `0999312/SlashBlade_Resharped@6e2a0a092fb794d7ea56fd83452869674f3ab1c7`, Minecraft 1.20.1, Resharped 1.9.65, Forge 47.4.0, player animator 1.0.2-rc1+1.20 as declared in gradle.properties.

## Resource paths and readers

`PlayerAnimationOverrider` registers 43 mappings. 41 use `slashblade:model/pa/player_motion.vmd`; Piercing and Piercing Just instead use `DefaultResources.testPLLocation`, which resolves to `slashblade:combostate/piercing_pl.vmd`. Names alone are misleading: this is not `test_pl.vmd`.

`VmdAnimation` loads `slashblade:model/pa/alex.pmd` through `MmdPmdModelMc`, which calls Minecraft's resource manager. It maps `leftArm/rightArm/leftLeg/rightLeg` to `left arm/right arm/left leg/right leg`. It reads the bone's local translation/quaternion; this is distinct from blade skinning. It applies special position scaling and rotation signs. Player time runs at the frame-to-tick conversion of 30 frames / 20 ticks. The class sets `loop=false` on tick, even for a mapping constructed as looping; resource data cannot repair that behavior.

The generated PMD has only `classic_root`, so the adapter's existing `bone == null` fallback returns `value0` for all player body parts. This preserves the underlying **modern vanilla** pose instead of freezing arms or pretending old whole-body VMD tracks exist. Neutral player VMD keys cover every fixed frame slot. This is an intentional approximation, not a reconstructed 1.12.2 body clip. The PMD is globally shared, including Piercing. Static LazyOptional caching requires a client restart after changing the pack.

`LayerMainBlade` loads each ComboState's motion through `BladeMotionManager`. The actual manager path is `client/renderer/model/BladeMotionManager.java`, not the hinted `.../util/` path. `MmdVmdMotionMc` uses Minecraft's resource manager; this proves normal pack override resolution at the code level. The manager caches by ResourceLocation, invalidating on TextureStitchEvent.Post; hot reload behavior is not claimed verified.

## Blade/saya transform

The installed `model/bladeholder.pmd` was inspected. All nine bind positions are (0,0,0); hierarchy:

| Root | Chain | Endpoint |
|---|---|---|
| センター | JointA1 → JointA2 → JointA3 | hardpointA (blade) |
| センター | JointB1 → JointB2 → JointB3 | hardpointB (saya) |

The bake resets intermediate bones and writes complete transformed poses to hardpointA/B. It inverts the modern layer's translation (0,1.5,0), motion scale 0.125, Z rotation 180° and X reflection. Tests reconstruct the resulting modern layer matrix against the sampled legacy transform. The modern final model scale remains 0.0078125, whereas the old combined model scale was 0.075 × 0.095 = 0.007125. Mesh size is therefore not exactly restored.

NyMmd `MotionData.getMotionPosRot` uses linear translation and quaternion slerp in this version, ignoring VMD Bezier interpolation bytes. The generic tool preserves those bytes; the procedural bake samples every integer frame to approximate the old nonlinear curve. Subframe interpolation remains an approximation.

## old_motion.vmd

`DefaultResources.BaseMotionLocation` declares `combostate/old_motion.vmd`; the pinned asset tree does not contain it. All 92 registered ComboStates were parsed: 87 resolve explicitly or by Builder default to ExMotionLocation (`motion.vmd`); five Piercing states use `piercing.vmd`. None resolves to BaseMotionLocation. Supplying old_motion.vmd alone cannot affect these built-in combos. This is a retained declaration with no callsite in the audited combo loading route; its historic removal reason has not been established, and no speculative claim is made.

## Playback mismatches that data cannot fix

Blade time follows timeout transitions and clamps inside each state's frame interval; player time starts at its registered start frame and runs the longer interval. `ComboState.getTimeoutMS` divides duration by speed, whereas the inspected layer's frame lookup uses raw elapsed time. Non-unit-speed moves can transition before a complete visual window plays. Shared states and Java callbacks also control body yaw, velocity and effects. These are documented limits, never patched with runtime code.
