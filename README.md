# SlashBlade Classic Motion Pack

Restore the classic SlashBlade 1.12.2 motion style on SlashBlade: Resharped for Minecraft 1.20.1.

**v0.1.0 experimental candidate — Runtime verification pending.** This is a resource pack, not a mod. It contains a source-derived classic blade/saya animation bake, a vanilla player-pose adapter, and generated classic-style attack-effect adapters. It does **not** contain recovered 1.12.2 skeletal animations: that version implements its blade motions procedurally in Java and has no VMD files.

## Requirements

- Minecraft 1.20.1
- SlashBlade: Resharped and its normal dependencies, including its player-animation support
- Target inspected: Resharped **1.9.65**, master commit `6e2a0a092fb794d7ea56fd83452869674f3ab1c7`

**No additional mod required.** No Java classes, scripts, datapacks or executable code ship in the ZIP.

## Installation

1. Download `SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip` from the PR/Actions build artifact (there is no verified stable Release yet).
2. Put the ZIP into `.minecraft/resourcepacks/` without extracting it.
3. Enable it above other packs that override SlashBlade animations/effects.
4. Restart the Minecraft client, enter a world and use SlashBlade.

The restart is necessary for a reliable test: Resharped caches the player PMD in a static lazy value. Enabling this pack after the model has loaded does not recreate that value. Restart after disabling it too. An enable-only hot swap has **not** been established.

## Animation and effect status

| Area | This build |
|---|---|
| A1, A2 | Legacy Saya1/Saya2 blade + sheath curves baked into 1–41 and 100–151; recovery adapted |
| A3–A5, A4 EX | Coherent classic S-rank motion language: SIai → SSlashEdge → SReturnEdge → SSlashBlade, fitted to modern shared/branching slots; approximate semantics |
| Air, Upper, Rapid, Rising, Judgement | Source-derived legacy visual candidates; runtime unverified |
| Void Slash | Dedicated modern **Classic Interpretation**: SlashDim-like attack stage + classic Noutou gesture in Resharped's separate sheath stage |
| B, Circle, C, Sakura, shared Drive/Wave slots | Shared-slot **Classic Interpretation** compromises; one VMD region must serve every modern consumer |
| Normal slash light / `EntitySlashEffect` | Global generated **Classic Trail Adapter** replaces modern `slash.obj/png` with a narrow tapered afterimage. This covers every `AttackManager.doSlash(...)` effect and Void Slash without per-combo Java changes |
| Drive projectile visual | r32's procedural 14-point Drive prism is baked into Resharped's fixed `drive.obj` transform; generated neutral `ss.png` keeps modern blade color tinting |
| Judgement Cut visual | Resharped already ships the exact r32 `slashdim.obj/png` Git blobs; the pack deliberately leaves them untouched instead of redistributing duplicate art |
| Player body | Modern custom full-body poses bypassed by a generated PMD adapter; underlying **1.20.1 vanilla poses** retained, not an exact 1.12.2 body restoration |
| Piercing | Upstream blade motion untouched; player pose adapter is global and also affects this move |
| Gameplay | Resharped damage, movement, timing, branches and effect entities remain authoritative |

The ground classic chain begins with two **saya strikes**. The shared A3 slot then uses old `SIai`; on Resharped's powered continuation the visual sequence proceeds through `SSlashEdge → SReturnEdge → SSlashBlade`. A resource pack cannot select Battou versus SIai dynamically from old rank/current modern power state, so the regular A4 path is an explicit compromise. The source has no old A1–A5 VMD slots to copy.

The project distinguishes **Classic Restoration** from **Classic Interpretation**. Restoration samples a directly corresponding r32 move or procedural visual. Interpretation keeps a modern Resharped move/state but expresses it using r32 motion/effect language. Modern frame sharing is machine-checked so improving one move cannot silently overwrite another move that consumes the same VMD frames. See [modern Classic Interpretation policy](docs/mapping/modern-classic-interpretation.md), [classic attack-effect adaptation](docs/mapping/classic-effect-adaptation.md), [source provenance](docs/research/legacy-1.12.2-source.md), [semantic mapping](docs/mapping/legacy-to-resharped.md), and [limitations](docs/limitations.md).

### Resource-pack effect ceiling

The pack can replace Resharped's hard-coded effect meshes/textures, but it cannot replace the Java entity renderer. For normal slash effects, Resharped still owns spawn timing, lifetime, `rotationOffset - 135° * progress`, scale/flattening, blade color and rank-dependent render passes. Drive and Judgement Cut likewise keep their modern entity timing/choreography. The new effect assets are therefore designed to remain visually coherent under those fixed transforms; they are not a claim that the old blade-attached `LayerSlashBlade` trail renderer is running on 1.20.1.

## Comparison and verification

The canonical motion source is the official SlashBlade 1.12.2/r32 branch. In addition, CI cross-checks the overlapping procedural move table and blade/saya transform math against the independent modern port [Old Dream Reforged](https://github.com/rianfalltwilight-lab/seac-slashblade-old-dream-reforged), pinned to a known commit. This is a validation oracle only: it is not a runtime dependency and its Java renderer is not shipped in the pack. See [Old Dream oracle research](docs/research/old-dream-reforged-oracle.md).

The current evidence is source analysis, independent sampled matrix comparisons, decoded-VMD matrix reconstruction, generated-effect geometry/texture checks, format checks and deterministic builds. No automated in-game comparison is claimed. The bodies, weapon attachment, first-person view, early cancels, remote players and final effect alignment need the [runtime checklist](docs/testing-checklist.md). This is not a claim to restore the complete 1.12.2 combat system or every animation exactly.

## Build (developers only)

Python 3.10+; no third-party Python dependencies:

```sh
python scripts/verify_old_dream_oracle.py
python -m unittest discover -s tests -v
python scripts/build_pack.py
python scripts/validate_pack.py dist/SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip
```

The build regenerates all shipped VMD/PMD and classic effect resources, writes an original geometric icon, validates the pack and creates a deterministic ZIP with `pack.mcmeta` at its root. Players do not run these tools. [Development details](docs/development.md).

## Credits and license

Classic procedural motion/effect reference: Furia / flammpfeil, SlashBlade `mc1.12-r32`, official `1.12.2` branch. Modern resource contracts: MMF-Group / 0999312, SlashBlade: Resharped. Independent validation reference: Old Dream Reforged, pinned and credited in `THIRD_PARTY_NOTICES.md`. The codec, packaging, generated classic trail art, generated neutral Drive texture and original metadata use this repository's MIT license. The legacy-derived motion and procedural Drive geometry retain their separately documented provenance and custom upstream terms; they are **not** relabeled MIT. No modern upstream VMD, PMD, texture or model binary is redistributed. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
