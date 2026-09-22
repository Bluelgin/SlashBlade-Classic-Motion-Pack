# Player pose adapter audit

The pack deliberately does **not** invent a 1.12.2 full-body animation. This note pins why the generated PMD/VMD pair is a valid resource-only passthrough for the inspected Resharped target.

## Legacy evidence

The official r32 source tree contains no full-body VMD/PMD animation atlas. SlashBlade restarts the normal Minecraft swing clock while `LayerSlashBlade` renders blade/sheath motion independently. Therefore there is no authoritative r32 skeletal clip to copy into modern A1–A5 frame windows.

## Resharped adapter behavior

Pinned target:

- `0999312/SlashBlade_Resharped@6e2a0a092fb794d7ea56fd83452869674f3ab1c7`
- `compat/playerAnim/VmdAnimation.java`
- `compat/playerAnim/PlayerAnimationOverrider.java`

`PlayerAnimationOverrider` installs a `VmdAnimation` at animation layer 0 whenever a mapped SlashBlade motion starts. `VmdAnimation.get3DTransform(...)` looks up the requested player model part in the PMD. Arm/leg names are mapped to PMD names such as `left arm` and `right leg`. If the PMD has no matching bone, execution falls through and returns the incoming `value0` unchanged.

That last behavior is the mechanism used by this pack.

## Generated adapter

`pack/assets/slashblade/model/pa/alex.pmd` is an original, valid, bone-only PMD containing exactly one deliberately unknown bone:

```text
classic_root
```

`player_motion.vmd` likewise contains only `classic_root` keys. It contains no `body`, `head`, arm or leg bone names that Resharped queries for player animation.

Consequently, for actual Minecraft player parts the target code cannot find a PMD bone and returns `value0`. The underlying player pose is therefore passed through instead of being replaced by Resharped's custom whole-body SlashBlade VMD pose.

This is stronger than a neutral animation authored against the real player bones. A real `right arm` bone with zero rotation would still enter the target's bone conversion path and could alter blending semantics. The intentionally missing-bone adapter avoids that path entirely.

## What it does and does not restore

| Area | Result |
|---|---|
| Suppress Resharped custom SlashBlade skeletal pose | `SUPPORTED` through missing-bone passthrough |
| Preserve incoming/underlying player transform | `SUPPORTED` by target `return value0` behavior |
| Recover a historical r32 full-body clip | `NOT AVAILABLE IN SOURCE` |
| Recreate every 1.12.2 vanilla player-render nuance | `NOT CLAIMED` |
| Change `PlayerAnimationOverrider` layer priority | `IMPOSSIBLE_RESOURCE_PACK_ONLY` |
| Prevent upstream layer-0 replacement interactions with other animation mods | `IMPOSSIBLE_RESOURCE_PACK_ONLY` |
| Reliable live PMD swap | No; the PMD is statically lazy-cached, so restart is required |

The adapter is therefore intentional project architecture, not a temporary placeholder waiting for a missing VMD to be found.
