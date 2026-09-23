# SlashBlade Classic Motion Pack

Restore the classic SlashBlade 1.12.2 motion style on SlashBlade: Resharped for Minecraft 1.20.1.

**v0.1.0 experimental candidate — Runtime verification pending.** This is a resource pack, not a mod. It contains a source-derived classic blade/saya animation bake, a vanilla player-pose adapter, dedicated Piercing classicization, slash-light suppression, and SA-art preservation. It does **not** contain recovered 1.12.2 skeletal animations: that version implements its blade motions procedurally in Java and has no VMD files.

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
| Void Slash | Dedicated modern **Classic Interpretation**: preparation until the modern tick-16 release, then SlashDim-like attack stage + classic Noutou gesture in Resharped's separate sheath stage |
| Piercing | Dedicated modern **Classic Interpretation**: Resharped's isolated `piercing.vmd` is replaced by r32 Stinger thrust language with source-timed delayed Noutou recovery; `piercing_pl.vmd` is replaced by the vanilla-body passthrough adapter |
| B, Circle, C, Sakura, shared Drive/Wave slots | Shared-slot **Classic Interpretation** compromises; one VMD region must serve every modern consumer |
| Normal slash light / `EntitySlashEffect` | **Suppressed by design.** The default pack overrides `slash.obj/png` with a microscopic valid mesh and fully transparent texture, so neither Resharped's modern slash disc nor the earlier simulated classic ribbon is shown. The effect entity and gameplay logic still run normally |
| Phantom Blade / Drive / Wave projectile visual | **Preserved from installed Resharped/addons.** The pack does not override `drive.obj` or `ss.png`; these are shared SA projectile-art resources used by 幻影刃, 幻影刃-纵, 波刀龙胆 and potentially third-party `EntityDrive` users |
| Judgement Cut visual | Resharped already ships the exact r32 `slashdim.obj/png` Git blobs; the pack deliberately leaves them untouched instead of redistributing duplicate art |
| Player body | Modern custom full-body poses bypassed by a generated PMD adapter; underlying **1.20.1 vanilla poses** retained, not an exact 1.12.2 body restoration |
| First-person attack motion | The same classic VMD blade/saya motion is visible through Resharped's blade layer; runtime clipping/alignment still needs in-game acceptance |
| First-person idle/hold camera transform | **`IMPOSSIBLE_RESOURCE_PACK_ONLY` on the pinned target.** Resharped resets the incoming item-render pose to identity and applies its own hard-coded first-person transform, so item-model `firstperson_*` display JSON cannot restore r32's old hold position/angle |
| Active main-hand standby | Frames 0–1 already use the source-derived r32 `None` blade/saya pose |
| Back/offhand carry poses | **`IMPOSSIBLE_RESOURCE_PACK_ONLY` on the pinned target.** Modern `CarryType` placement is hard-coded in Java and does not consume the VMD |
| Attack / sheath audio | **Exact r32 orchestration is `IMPOSSIBLE_RESOURCE_PACK_ONLY` without global vanilla-sound side effects.** r32 and Resharped select different vanilla SoundEvents/pitch/timing in Java; the default pack does not replace trident/chain/etc. sounds globally |
| Gameplay | Resharped damage, movement, timing, branches and effect entities remain authoritative |

The ground classic chain begins with two **saya strikes**. The shared A3 slot then uses old `SIai`; on Resharped's powered continuation the visual sequence proceeds through `SSlashEdge → SReturnEdge → SSlashBlade`. A resource pack cannot select Battou versus SIai dynamically from old rank/current modern power state, so the regular A4 path is an explicit compromise. The source has no old A1–A5 VMD slots to copy.

Piercing has its own independent modern atlas, so it can be classicized without stealing frames from the main chain. Frames 1–32 stay in the r32 neutral blade/saya pose; frame 33 switches to old `Stinger`, matching the modern Java lunge start. Stinger's 20-tick r32 reset clock lands at VMD frame 63, where a fresh `Noutou` recovery begins. The six-tick Noutou swing reaches its final pose at frame 72, that pose is held through 77 because r32 entered Noutou with a delayed `LastActionTime`, and frame 78 returns to neutral. Forward movement, hit timing, just timing and sound remain Resharped behavior.

The project distinguishes **Classic Restoration** from **Classic Interpretation**. Restoration samples a directly corresponding r32 move or procedural visual. Interpretation keeps a modern Resharped move/state but expresses it using r32 motion/effect language. Modern frame sharing is machine-checked so improving one move cannot silently overwrite another move that consumes the same VMD frames. See [modern Classic Interpretation policy](docs/mapping/modern-classic-interpretation.md), [Piercing interpretation](docs/research/piercing-classic-interpretation.md), [attack-effect adaptation](docs/mapping/classic-effect-adaptation.md), [source provenance](docs/research/legacy-1.12.2-source.md), [semantic mapping](docs/mapping/legacy-to-resharped.md), [first-person renderer audit](docs/research/first-person-rendering.md), [standby/carry audit](docs/research/standby-carry-rendering.md), and [limitations](docs/limitations.md).

### First-person ceiling

The old r32 view is not just an item-model transform. `BladeFirstPersonRender` applies its own Java matrix, has a separate Projectile Barrier branch, synchronizes pitch and controls first-person blur behavior. On the pinned Resharped target, the modern `BladeFirstPersonRender` resets the incoming `PoseStack` to identity before applying its own fixed matrix and invoking `LayerMainBlade`. Therefore the pack can classicize the **attack motion seen in first person**, but cannot independently replace the outer camera-relative idle/hold transform without runtime code. A global OBJ/PMD/VMD offset would also move the third-person blade and is rejected as a regression, not treated as a valid workaround.

### Resource-pack effect ceiling

The pack can replace Resharped's hard-coded effect meshes/textures, but it cannot replace the Java entity renderer. r32's classic trail was attached to the blade renderer, while Resharped's `EntitySlashEffect` owns a separate progress rotation, lifetime, scale/flattening, color and rank passes. The earlier simulated classic ribbon therefore remained visibly out of sync with the restored weapon motion in runtime testing. The default pack now suppresses that shared slash-light visual entirely rather than pretending to restore a renderer that a resource pack cannot reproduce. Because `slash.obj/png` are also shared by SA consumers such as Circle Slash, Sakura End and Void Slash, this suppression cannot be limited to ordinary attacks in a resource pack. By contrast, `drive.obj/ss.png` are no longer overridden at all: runtime testing showed that doing so rewrote Phantom Blade-class SA sword-qi art.

### Resource-pack audio ceiling

Classic r32 attack sound is not simply a SlashBlade-owned `.ogg` bank. The pinned source frequently calls vanilla Minecraft SoundEvents with distinctive runtime parameters; the ordinary r32 SlashBlade attack path, for example, uses player sweep at volume `0.8` and pitch `0.01`. Resharped instead uses modern Java-selected sounds such as trident throw for slash/Piercing effects and chain hit for quick sheath actions. A resource pack can replace the files behind those vanilla events, but it cannot change the event selected by Java, the per-call pitch/volume or the callback tick. Replacing the vanilla files would also change normal Minecraft tridents/chains globally, so the default pack deliberately leaves those sounds alone.

## Comparison and verification

The canonical motion source is the official SlashBlade 1.12.2/r32 branch. In addition, CI cross-checks the overlapping procedural move table and blade/saya transform math against the independent modern port [Old Dream Reforged](https://github.com/rianfalltwilight-lab/seac-slashblade-old-dream-reforged), pinned to a known commit. This is a validation oracle only: it is not a runtime dependency and its Java renderer is not shipped in the pack. See [Old Dream oracle research](docs/research/old-dream-reforged-oracle.md).

The current evidence is source analysis, independent sampled matrix comparisons, decoded-VMD matrix reconstruction, generated-effect geometry/texture checks, dedicated Piercing binary checks, format checks and deterministic builds. No automated in-game comparison is claimed. The bodies, weapon attachment, first-person attack visibility/clipping, early cancels, remote players and final effect alignment need the [runtime checklist](docs/testing-checklist.md). The r32 first-person idle/hold matrix and runtime back/offhand carry transforms are documented `IMPOSSIBLE_RESOURCE_PACK_ONLY` boundaries on the pinned Resharped renderer rather than unfinished asset work. This is not a claim to restore the complete 1.12.2 combat system or every animation exactly.

## Build (developers only)

Python 3.10+; no third-party Python dependencies:

```sh
python scripts/verify_old_dream_oracle.py
python -m unittest discover -s tests -v
python scripts/build_pack.py
python scripts/validate_pack.py dist/SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip
```

The build regenerates all shipped VMD/PMD and effect resources, writes an original geometric icon, validates the pack and creates a deterministic ZIP with `pack.mcmeta` at its root. `pack/` is only generated staging; a fresh checkout intentionally keeps just its static `pack.mcmeta`, so do not zip that directory before running the build. Players do not run these tools. [Development details](docs/development.md).

## Credits and license

Classic procedural motion/effect reference: Furia / flammpfeil, SlashBlade `mc1.12-r32`, official `1.12.2` branch. Modern resource contracts: MMF-Group / 0999312, SlashBlade: Resharped. Independent validation reference: Old Dream Reforged, pinned and credited in `THIRD_PARTY_NOTICES.md`. The codec, packaging, generated slash-suppression assets and original metadata use this repository's MIT license. The legacy-derived motion data retains its separately documented provenance and custom upstream terms; it is **not** relabeled MIT. No modern upstream VMD, PMD, texture or model binary is redistributed. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
