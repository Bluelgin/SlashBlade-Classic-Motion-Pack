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
| Sheathe | Old Noutou plus short recovery bridges; saya-only return is an adapted bridge | APPROXIMATE |
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

The A3 classic 12-tick reset window still lands exactly on Resharped's frame-218 A3 state boundary (30 VMD frames / 20 game ticks), so changing the source motion does not invalidate the established recovery boundary.

## Shared-slot decisions

- A1_END2 replays 21–41 and therefore necessarily sees A1 recovery.
- B2–B7 share 710 onward; Circle starts at 725. The candidate samples repeated SSlashBlade motions at those entry points so they do not become static holds. Reset jumps are possible and need runtime refinement.
- Sakura right uses A3 subranges, with finish extending to 314; because it shares A3's atlas region it also receives the SIai candidate. This is a deliberate shared-slot compromise.
- Sakura left and Aerial Cleave landing share 1816–1859. The loop 1812–1817 stays held; a Kiriorosi approximation begins at 1818. This does not recreate two independent moves.
- Horizontal Drive shares C; Vertical Drive and Wave Edge share Upper Slash. Their projectiles remain Java-driven.
- Judgement's actual slash window begins at 1923, so the SlashDim swing is placed there, not in the preparation window. This one five-frame slot compresses the visual; non-unit speed timeout transitions remain a limitation.
- Normal A4 does not lead directly to A5. The powered branch uses A4_EX → A5; testing must exercise both.

## Milestone state

A1 blade/saya data is implemented and statically verified in the modern window. A1–A5 candidates are generated. These are not runtime-accepted milestones. The specifically requested recovered A1 skeletal player clip cannot be asserted because the identified official legacy source does not contain one; the current body solution is explicitly an approximation. No complete move is claimed 100% restored.
