# Legacy → Resharped semantic mapping

Classification describes the resource adaptation, not an in-game pass.

- EXACT: identical visual data/semantics proven; no complete move is awarded this status here.
- REMAP: a same-purpose legacy blade/saya motion is sampled into modern slots; timing/recovery/mesh differences remain.
- APPROXIMATE: a legacy pose family is reused where modern semantics or shared windows differ.
- IMPOSSIBLE_RESOURCE_PACK_ONLY: the requested behavior is controlled by Java gameplay logic.

Player bodies for every row use the separately documented vanilla-pose adapter, not old skeletal clips. There are no old VMD frame indexes; source normalized swing time is 0–1. The tool samples actual r32 rendering equations.

| Modern family | Old ComboSequence | Modern atlas frames | Classification |
|---|---|---|---|
| A1 | Saya1 | 1–41 | REMAP |
| A2 | Saya2 | 100–151 | REMAP |
| A3 / Sakura right | SIai | 200–314 | APPROXIMATE |
| C / Drive horizontal | Battou | 400–488 | APPROXIMATE |
| A4 | SSlashEdge | 500–608 | APPROXIMATE |
| B / Circle | SSlashBlade | 700–787 | APPROXIMATE |
| A4 EX | SSlashEdge + SReturnEdge | 800–894 | APPROXIMATE |
| A5 | SSlashBlade | 900–1061 | APPROXIMATE |
| Aerial A1 | ASlashEdge | 1100–1132 | REMAP |
| Aerial A2 / Sakura right air | AKiriorosi | 1200–1241 | REMAP |
| Aerial A3 / Sakura left air | AKiriorosiFinish | 1300–1338 | REMAP |
| Aerial B3 | AKiriorosiB | 1400–1443 | REMAP |
| Aerial B4 | AKiriage | 1500–1547 | REMAP |
| Upper / Drive vertical / Wave Edge | Kiriage | 1600–1693 | REMAP |
| Upper jump | Kiriage | 1700–1717 | APPROXIMATE |
| Cleave / Sakura left | HelmBraker | 1800–1886 | APPROXIMATE |
| Judgement Cut | SlashDim | 1900–1963 | REMAP |
| Rapid Slash | RapidSlash | 2000–2073 | REMAP |
| Rising Star | RisingStar | 2100–2147 | REMAP |
| Void Slash | SlashDim | 2200–2299 | APPROXIMATE |

| Additional behavior | Source or treatment | Classification |
|---|---|---|
| Guard / A1_END2 | Shared A1 recovery; old ProjectileBarrier uses Java-driven rotations/effects, not an independent compatible clip | APPROXIMATE |
| Idle | Old None placement; underlying modern vanilla body | REMAP |
| Draw | SIai at A3; source says earlier ground attacks are saya strikes | APPROXIMATE |
| Sheathe / timeout | Source-timed moves now follow r32 state transitions: saya and SlashDim/Iai/SIai reset to None; other blade moves enter Noutou and restart the six-tick vanilla swing | REMAP / APPROXIMATE by shared slot |
| Sprint/air movement | Existing modern body and entity movement | IMPOSSIBLE_RESOURCE_PACK_ONLY |
| Piercing | Modern blade asset unchanged; old Stinger is only a researched future candidate | APPROXIMATE (not restored) |
| Damage, impacts, invulnerability, cancel windows, entity velocity | Java state/action callbacks | IMPOSSIBLE_RESOURCE_PACK_ONLY |

## Ground-chain branch compromise

The old r32 right-click chain is state-sensitive. Its iconic high-rank route is:

`Saya1 → Saya2 → SIai → SSlashEdge → SReturnEdge → SSlashBlade`

while the ordinary branch after `Saya2` can use `Battou` instead. Resharped makes its powered/unpowered choice **after** its shared `COMBO_A3` state: A3 proceeds to normal A4 or powered A4 EX, and only the powered A4 EX path continues to A5. A resource pack cannot inspect that runtime power/rank decision and select two different VMD clips for the same A3 frame range.

The pack therefore chooses `SIai` for the shared A3 window. This gives the powered modern path a coherent classic sequence:

`A1 Saya1 → A2 Saya2 → A3 SIai → A4 EX (SSlashEdge + SReturnEdge) → A5 SSlashBlade`

It is also a better temporal fit for modern A3 than the previous Battou candidate: modern A3 performs two timeline slash actions, while old `SIai` uses the draw-and-return progress curve (`0 → 1 → 0`) during one swing. The regular A4 branch then continues visually with `SSlashEdge` but ends early; that is explicitly an approximation, not a claim that modern power state equals old Stylish Rank.

## Classic reset clocks and timeout targets

The visible old swing is sampled on the vanilla six-tick swing curve; `comboResetTicks` is a separate state timeout. Earlier candidates let modern END states hold a completed legacy pose far beyond that old timeout. That was especially visible on A4 EX/A5 and made the weapon feel suspended after the hit.

For source-timed slots the bake converts the pinned r32 timeout with `30 VMD fps / 20 game tps`. Delayed mappings start that clock when the mapped legacy move starts, not when the modern atlas slot starts. Compound slots use the final embedded move: A4 EX therefore times recovery from `SReturnEdge` at frame 817, and Cleave/Sakura-left from the embedded `Kiriorosi` at frame 1818.

The resulting source-derived timeout frames are:

| Family | Timeout frame | r32 move owning the clock |
|---|---:|---|
| A1 | 31 | Saya1 |
| A2 | 130 | Saya2 |
| A3 / Sakura right | 218 | SIai |
| C / Drive horizontal | 418 | Battou |
| A4 | 546 | SSlashEdge |
| B / Circle | 763 | final SSlashBlade segment |
| A4 EX | 855 | SReturnEdge |
| A5 | 956 | SSlashBlade |
| Aerial A2 | 1238 | AKiriorosi |
| Aerial A3 | 1338 | AKiriorosiFinish |
| Aerial B3 | 1438 | AKiriorosiB |
| Aerial B4 | 1518 | AKiriage |
| Upper / Drive vertical / Wave Edge | 1630 | Kiriage |
| Cleave / Sakura left | 1836 | Kiriorosi |
| Judgement Cut | 1935 | SlashDim |
| Rapid Slash | 2018 | RapidSlash |
| Rising Star | 2118 | RisingStar |
| Void Slash | 2212 | SlashDim |

`ItemSlashBlade.onUpdate` also distinguishes what happens **after** that timeout. `Saya1`/`Saya2` and `SlashDim`/`Iai`/`SIai` reset directly to `None`; they do not play a made-up sheathe clip. Other mapped non-saya moves transition to `Noutou` and call `doSwingItem`, so the bake starts the old Noutou pose immediately and gives it one fresh six-tick / nine-VMD-frame swing before returning to neutral.

This matters for the current ground chain: A3/SIai now becomes neutral at frame 218 instead of incorrectly entering Noutou, while A4/A4 EX/A5 still perform the classic Noutou timeout path. Judgement Cut and Void Slash likewise reset directly from SlashDim to neutral.

Aerial A1 and Upper jump are deliberately excluded from `legacy_reset`: their Resharped atlas windows end before the corresponding r32 reset clock can fit. They remain explicit resource-pack timing approximations rather than silently claiming a clamped timeout is exact.

## Shared-slot decisions

- A1_END2 replays 21–41 and therefore sees A1's r32 timeout at frame 31. Frames 31 onward are neutral, matching the old saya-state reset rather than reversing the saya curve.
- B2–B7 share 710 onward; Circle starts at 725. Repeated SSlashBlade samples remain a compromise, but the final shared segment now uses its r32 reset clock at frame 763 before entering Noutou.
- Sakura right uses A3 subranges, with finish extending to 314; because it shares A3's atlas region it also receives SIai and the direct-to-None timeout at frame 218. This is a deliberate shared-slot compromise.
- Sakura left and Aerial Cleave landing share 1816–1859. The loop 1812–1817 stays held; a Kiriorosi approximation begins at 1818 and owns the source reset at 1836. This does not recreate two independent moves.
- Horizontal Drive shares C; Vertical Drive and Wave Edge share Upper Slash. Their projectiles remain Java-driven even though the visual timeout is source-timed.
- Judgement's actual slash window begins at 1923, so SlashDim is placed there rather than in the preparation window. Its r32 eight-tick timeout lands at 1935 and resets directly to None. The five-frame modern swing window still compresses the visual.
- Normal A4 does not lead directly to A5. The powered branch uses A4_EX → A5; testing must exercise both.

## Milestone state

A1 blade/saya data is implemented and statically verified in the modern window. A1–A5 candidates, air candidates and major special-action candidates are generated. Source timing and timeout-state behavior are now guarded by tests, but runtime acceptance still depends on Minecraft testing. The specifically requested recovered skeletal player clips cannot be asserted because the identified official legacy source does not contain them; the current body solution is explicitly an approximation. No complete move is claimed 100% restored.
