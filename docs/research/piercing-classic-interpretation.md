# Piercing Classic Interpretation

This project targets SlashBlade: Resharped 1.9.65 at `0999312/SlashBlade_Resharped@6e2a0a092fb794d7ea56fd83452869674f3ab1c7`.

Piercing is structurally different from the main combo atlas. Resharped gives it two dedicated resources:

- `slashblade:combostate/piercing.vmd` for blade/sheath motion;
- `slashblade:combostate/piercing_pl.vmd` for the player animation consumer.

The pinned combo windows are:

| Modern state | Frames |
|---|---:|
| `piercing` | 1–33 |
| `piercing_2` | 33–55 |
| `piercing_just` | 34–55 |
| `piercing_end` | 55–65 |
| `piercing_end2` | 65–90 |

`piercing_2`/`piercing_just` own the real Java lunge: during the first three elapsed ticks Resharped moves the entity forward and performs an area hit, and at elapsed tick 1 it plays the Piercing sound. The Resource Pack does not change any of that gameplay.

## Classic mapping

Official r32 does not have this modern Piercing state machine or a dedicated Piercing VMD. The closest source move is `Stinger` (same procedural table values as the old thrust family):

- non-scabbard move;
- amplitude `180`;
- direction `180`;
- `comboResetTicks = 20`;
- old renderer forces Stinger progress to `1.0`, so the blade is shown at the fully committed thrust pose while gameplay motion supplies the lunge.

For that reason Piercing is classified as `CLASSIC_INTERPRETATION`, not `CLASSIC_RESTORATION`.

The generated blade atlas is:

```text
frames  0..32   r32 None pose (modern preparation/hold)
frame      33   switch to full r32 Stinger thrust pose
frames 33..62   hold Stinger while modern Java owns forward movement / hit
frame      63   r32 Stinger reset clock expires -> fresh Noutou
frames 63..71   Noutou swing
frames 72..90   r32 None pose
```

The recovery frame is source-derived: `33 + round(20 ticks * 30 VMD fps / 20 game tps) = 63`.

This timing also lands naturally inside Resharped's `piercing_end`/`piercing_end2` handoff. The modern quick-sheath sound at frame 65 remains Java-owned and occurs during the generated Noutou gesture.

## Player body strategy

`piercing_pl.vmd` is replaced with the same bone-only passthrough strategy used by the main player adapter: only `classic_root` is keyed. r32 shipped no dedicated skeletal Piercing clip to recover, so the pack deliberately avoids inventing a modern-looking full-body replacement. The visible lunge still comes from Resharped's actual movement code.

This means:

- classic blade/saya thrust language: supported;
- removal of Resharped's dedicated full-body Piercing VMD pose: supported;
- forward displacement / area hit / just timing / sound / cancel logic: modern Java remains authoritative;
- exact r32 body pose for a move that did not exist as this modern state machine: not claimed.

## Resource-only boundary

Because both Piercing resources are separate hard-coded VMD paths, this adaptation does not consume or collide with the main `motion.vmd` frame atlas. It is one of the safest modern moves to classicize in a pure Resource Pack.
