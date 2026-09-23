# Attack-effect adaptation

This document defines the resource-pack-only visual policy for attack effects on the pinned SlashBlade: Resharped 1.20.1 target (`6e2a0a092fb794d7ea56fd83452869674f3ab1c7`). It is intentionally separate from the VMD motion mapping.

## Why the normal slash light is suppressed

The classic blade/saya bake changes the weapon path substantially. Resharped's modern `EntitySlashEffect` is a separately animated effect entity: Java owns its lifetime, progress rotation, flattening, scale, rank passes and color. r32's classic trail was instead attached to the blade renderer and followed the actual blade motion.

A first resource-only attempt replaced Resharped's radial slash mesh with a narrow classic-style ribbon. Runtime testing showed that the result still looked wrong because the modern effect entity continued its own Java rotation independently of the restored blade motion. The default pack therefore suppresses this shared slash-light visual instead of shipping a fake classic trail.

## Shared-resource warning

The `SlashEffectRenderer` has only one hard-coded `slash.obj/png` pair. That resource is not limited to ordinary attacks. Base Resharped also creates `EntitySlashEffect` from Slash Arts such as Circle Slash, Sakura End and Void Slash, and third-party addons may reuse the same entity. A pure resource pack cannot tell which caller created a given instance.

Therefore slash-light suppression is intentionally **global to EntitySlashEffect**. It cannot mean “hide only ordinary attack lights but preserve every SA that happens to use the same renderer.”

A separate collision was found during runtime testing: `DriveRenderer` uses one hard-coded `drive.obj` + `ss.png` pair for `EntityDrive`. Those resources are the visible projectile art for 幻影刃 (`drive_horizontal`), 幻影刃-纵 (`drive_vertical`), 波刀龙胆 (`wave_edge`) and any addon that reuses `EntityDrive`. The earlier classic-Drive experiment therefore rewrote SA sword-qi art. That override has been removed.

## Effect families

| Runtime family | Resharped resource contract | Pack policy | Coverage |
|---|---|---|---|
| `EntitySlashEffect` / `SlashEffectRenderer` | `slashblade:model/util/slash.obj`, `slash.png` | **Visual suppression**: microscopic valid mesh + fully transparent texture | Ordinary `AttackManager.doSlash(...)` plus any SA/addon that uses `EntitySlashEffect`, including Circle Slash, Sakura End and Void Slash |
| `EntityDrive` / `DriveRenderer` | `slashblade:model/util/drive.obj`, `ss.png` | **Preserve installed SA art**: do not override | 幻影刃, 幻影刃-纵, 波刀龙胆 and third-party `EntityDrive` users |
| `EntityJudgementCut` / `JudgementCutRenderer` | `slashblade:model/util/slashdim.obj`, `slashdim.png` | **Already classic upstream**: do not duplicate | Judgement Cut dimension effect |

The machine-readable version is `data/effect_resource_contract.json`.

## Normal slash-light suppression

Simply deleting `slash.obj/png` from this pack would make Minecraft fall back to Resharped's original modern slash light, so the files remain as overrides. `scripts/generate_effects.py` emits a tiny non-degenerate four-vertex `base` quad and a fully transparent 1x1 RGBA texture.

This changes only the rendered `EntitySlashEffect` mesh/texture. The entity still exists and Resharped remains authoritative for gameplay, timing, networking, sounds and any non-model behavior.

## Drive / Phantom Blade policy

The pack does **not** ship `drive.obj` or `ss.png`.

Although r32 had a procedural Drive prism that can be reconstructed mathematically, replacing the modern fixed resources globally also replaces the user-visible projectile art of Phantom Blade-class Slash Arts. Runtime testing showed that this was a compatibility regression, so preservation of SA art takes priority over forcing a classic projectile silhouette.

## Judgement Cut

No visual replacement is needed for the model/texture contract. Resharped and r32 have identical Git blob IDs for both files:

- `slashdim.obj`: `9ab8de31a33970b884df9f4683ece271e9f12889`
- `slashdim.png`: `b79daa73dd545d0a8c3c41c845b083055bd7481a`

The installed Resharped copy is left untouched.

## Resource-pack ceiling

A resource pack cannot select effect resources by Java caller. All `EntitySlashEffect` instances share one `slash.obj/png`, and all `EntityDrive` instances share one `drive.obj/ss.png`. Spawn timing, lifetime, rotation, rank passes, color, hitboxes, damage, particles, sounds and networking remain Java-owned.

This is why the current default makes two different choices: suppress the shared slash-light renderer because the user prefers no mismatched blade light, but preserve Drive/Judgement SA art rather than globally rewriting their projectile visuals.

## Build/validation

CI verifies that:

- `slash.obj/png` are present, microscopic/transparent and cannot fall back to the modern slash disc;
- `drive.obj`, `ss.png`, `slashdim.obj` and `slashdim.png` are **absent from the pack**, preventing accidental SA-art overrides;
- VMD/PMD animation assets remain unchanged by this policy;
- no Java/Mixin/script/datapack runtime component is introduced.

Runtime visual acceptance remains an in-game check.
