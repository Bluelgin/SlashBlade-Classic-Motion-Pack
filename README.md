# SlashBlade Classic Motion Pack

Restore the classic SlashBlade 1.12.2 motion style on SlashBlade: Resharped for Minecraft 1.20.1.

**v0.1.0 experimental candidate — Runtime verification pending.** This is a resource pack, not a mod. It contains a source-derived classic blade/saya animation bake and a vanilla player-pose adapter. It does **not** contain recovered 1.12.2 skeletal animations: that version implements its blade motions procedurally in Java and has no VMD files.

## Requirements

- Minecraft 1.20.1
- SlashBlade: Resharped and its normal dependencies, including its player-animation support
- Target inspected: Resharped **1.9.65**, master commit `6e2a0a092fb794d7ea56fd83452869674f3ab1c7`

**No additional mod required.** No Java classes, scripts, datapacks or executable code ship in the ZIP.

## Installation

1. Download `SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip` from the PR/Actions build artifact (there is no verified stable Release yet).
2. Put the ZIP into `.minecraft/resourcepacks/` without extracting it.
3. Enable it above other packs that override SlashBlade animations.
4. Restart the Minecraft client, enter a world and use SlashBlade.

The restart is necessary for a reliable test: Resharped caches the player PMD in a static lazy value. Enabling this pack after the model has loaded does not recreate that value. Restart after disabling it too. An enable-only hot swap has **not** been established.

## Animation status

| Area | This build |
|---|---|
| A1, A2 | Legacy Saya1/Saya2 blade + sheath curves baked into 1–41 and 100–151; recovery adapted |
| A3–A5, A4 EX | Legacy Battou / SSlashEdge / SReturnEdge / SSlashBlade mapped to modern slots; approximate semantics |
| Air, Upper, Rapid, Rising, Judgement | Source-derived legacy visual candidates; runtime unverified |
| B, Circle, C, Void, Sakura, shared Drive/Wave slots | Explicit approximations and shared-slot compromises |
| Player body | Modern custom full-body poses bypassed by a generated PMD adapter; underlying **1.20.1 vanilla poses** retained, not an exact 1.12.2 body restoration |
| Piercing | Upstream blade motion untouched; player pose adapter is global and also affects this move |
| Gameplay | Resharped damage, movement, timing, branches and effects remain authoritative |

The ground classic chain begins with two **saya strikes**, followed by a draw. The source has no old A1–A5 VMD slots to copy. See [source provenance](docs/research/legacy-1.12.2-source.md), [semantic mapping](docs/mapping/legacy-to-resharped.md), and [limitations](docs/limitations.md).

## Comparison and verification

The canonical motion source is the official SlashBlade 1.12.2/r32 branch. In addition, CI cross-checks the overlapping procedural move table and blade/saya transform math against the independent modern port [Old Dream Reforged](https://github.com/rianfalltwilight-lab/seac-slashblade-old-dream-reforged), pinned to a known commit. This is a validation oracle only: it is not a runtime dependency and its Java renderer is not shipped in the pack. See [Old Dream oracle research](docs/research/old-dream-reforged-oracle.md).

The current evidence is source analysis, independent sampled matrix comparisons, format checks and deterministic builds. No in-game comparison footage or GUI test is claimed. The bodies, weapon attachment, first-person view, early cancels and remote players need the [runtime checklist](docs/testing-checklist.md). This is not a claim to restore the complete 1.12.2 combat system or every animation exactly.

## Build (developers only)

Python 3.10+; no third-party Python dependencies:

```sh
python scripts/verify_old_dream_oracle.py
python -m unittest discover -s tests -v
python scripts/build_pack.py
python scripts/validate_pack.py dist/SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip
```

The build regenerates all shipped VMD/PMD files, writes an original geometric icon, validates the pack and creates a deterministic ZIP with `pack.mcmeta` at its root. Players do not run these tools. [Development details](docs/development.md).

## Credits and license

Classic procedural motion reference: Furia / flammpfeil, SlashBlade `mc1.12-r32`, official `1.12.2` branch. Modern resource contracts: MMF-Group / 0999312, SlashBlade: Resharped. Independent validation reference: Old Dream Reforged, pinned and credited in `THIRD_PARTY_NOTICES.md`. The codec, packaging and original metadata use this repository's MIT license. The legacy-derived motion data retains its separately documented provenance and custom upstream terms; it is **not** relabeled MIT. No modern upstream VMD, PMD, texture or model binary is redistributed. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
