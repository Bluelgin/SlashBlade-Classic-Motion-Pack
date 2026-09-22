# Modern moves: Classic Interpretation

The pack has two deliberately different adaptation goals.

## 1. Classic Restoration

`CLASSIC_RESTORATION` is used when the pinned r32 source has a directly corresponding classic move family. The old procedural blade/saya transform is sampled and retargeted into a compatible Resharped VMD window. This is still normally classified as `REMAP` rather than `EXACT`, because modern state timing, meshes and player-body behavior differ.

Examples include Saya1/Saya2, the S-rank ground chain, AerialRave-family motions, RapidSlash and RisingStar.

## 2. Classic Interpretation

`CLASSIC_INTERPRETATION` is for a modern Resharped semantic move, or for a modern atlas region whose meaning is shared with another move. The modern gameplay/state remains untouched. Only the visible blade/saya motion is re-expressed using r32 motion language.

This is not a claim that the modern move existed in 1.12.2. The target is instead: **if this modern move had been animated by the classic procedural renderer, what would be a coherent visual interpretation?**

The machine-readable policy is `data/modern_classic_policy.json`; atlas overlap rules are implemented in `tools/slot_topology.py` and enforced by `tests/test_modern_policy.py`.

## Atlas topology categories

### Independent interpretation

A family owns a dedicated `motion.vmd` range with no other semantic consumer sharing two or more frames. It can receive a purpose-built classic-style sequence without changing another move.

The first pilot is Void Slash. Resharped gives it a dedicated region:

- `VOID_SLASH`: 2200–2277
- `VOID_SLASH_SHEATH`: 2278–2299

The pack now interprets these as two distinct modern states:

1. `2200–2277`: SlashDim-like attack language. The classic SlashDim timeout still returns to neutral.
2. `2278–2299`: a fresh classic Noutou gesture for the modern sheath state, then neutral at the r32 Noutou reset clock.

This preserves the modern two-stage structure while keeping both stages visually in the old renderer's vocabulary. It intentionally differs from claiming that r32 SlashDim itself transitioned to Noutou; it did not.

### Shared-slot interpretation

If two modern semantic families consume the same VMD frames, a resource pack cannot select a different pose based on runtime `ComboState`. Those families must share one compatible classic-style motion.

Pinned Resharped 1.20.1 examples:

| Modern semantic family | Shared atlas consumer | Current classic anchor |
|---|---|---|
| Sakura End Right (ground) | Combo A3 | SIai |
| Sakura End Left (ground) | Aerial Cleave landing | HelmBraker / Kiriorosi |
| Sakura End Right (air) | Aerial Rave A2 | AKiriorosi |
| Sakura End Left (air) | Aerial Rave A3 | AKiriorosiFinish |
| Drive Horizontal | Combo C | Battou |
| Drive Vertical | Upper Slash | Kiriage |
| Wave Edge Vertical | Upper Slash / Drive Vertical | Kiriage |

A one-frame boundary touch is not treated as a shared animation window. Resharped often ends one state on the same frame at which another begins; topology checks require at least two common frames before declaring a resource-only conflict.

## Java-only behavior

The policy also records behavior that cannot be independently restored or interpreted by `motion.vmd` alone:

- runtime branch decisions such as powered/unpowered A3 continuation;
- damage, hitboxes, invulnerability and cancel windows;
- entity movement/velocity;
- Drive/Wave Edge projectile creation and target logic;
- dynamic barrier/trail behavior whose timing is calculated in Java.

The resource pack may make the animation around these actions look classic, but it does not claim to reproduce their runtime mechanics.

## Why this distinction matters

Without this split, a project can accidentally label an invented modern animation as a recovered 1.12.2 asset, or break one move while improving another move that secretly shares the same VMD frames. The Restoration/Interpretation policy makes both cases explicit and testable.

Future modern-only work should prefer independent atlas regions first. Shared regions should only change after every meaningful consumer of the affected frames has been reviewed together.
