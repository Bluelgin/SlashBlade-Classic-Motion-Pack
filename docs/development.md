# Development

Runtime output is a normal resource pack. Nothing under tools/, scripts/, tests/ or docs/ is shipped. Existing root MIT copyright is retained.

## Source refresh

Check out `0999312/SlashBlade_Resharped` at `6e2a0a092fb794d7ea56fd83452869674f3ab1c7`, then run:

```sh
python scripts/extract_frame_maps.py /path/to/SlashBlade_Resharped
```

The extractor resolves Builder defaults and explicit resource constants and fails if a registration is not parsed. It emits 43 player entries and 92 blade entries. The full source asset inventory is recorded separately; upstream assets are not build dependencies or copied into the pack.

Legacy constants are pinned in `data/legacy_motion_map.json`, from the 34 ComboSequence definitions. Frame plan and approximation labels are in `data/bake_slots.json`. The dedicated modern Piercing atlas is pinned separately in `data/piercing_classic_policy.json`: blade frames 1–90 are generated into `combostate/piercing.vmd`, and the matching player resource `combostate/piercing_pl.vmd` is generated as a passthrough track. A build needs no network access or proprietary binary inputs.

To re-extract those constants, run `python scripts/extract_legacy_map.py /path/to/pinned-legacy-source`. It parses numeric expressions without executing Java or arbitrary Python input and preserves the optional legacy `mainHandCombo` reference used by r32 timeout semantics.

The first-person renderer contract is pinned separately in `data/first_person_render_contract.json`. It records the r32 `FPVOldStryleLike` matrix, Projectile Barrier branch, the pinned Resharped first-person matrix and the resource-pack capability classification. See `docs/research/first-person-rendering.md`. Because the modern renderer resets the incoming `PoseStack` to identity, item-model `firstperson_*` display transforms are not a valid override path for the pinned target; do not add such a file and claim FPV restoration without a source change that makes the assumption true.

## Generated pack staging

`pack/` is a build staging directory, **not** a checked-in copy of the current runtime ZIP. Only `pack/pack.mcmeta` is static source data. `scripts/build_pack.py` deletes every other staging entry before each build, regenerates the VMD/PMD/effect assets and icon, then copies the root README/license/notices into the staging tree before validation and packaging.

This is deliberate: keeping old generated binaries in Git allowed the source tree to become a misleading partial resource pack after new generated resources such as Piercing and the effect adapters were added. Do not zip a fresh repository checkout's `pack/` directory directly. Run the build and use the ZIP under `dist/`, or use the CI artifact.

## VMD tooling

After running a build, generated files can be inspected with:

```sh
python -m tools.vmd inspect pack/assets/slashblade/combostate/motion.vmd
python -m tools.vmd inspect pack/assets/slashblade/combostate/piercing.vmd
python -m tools.vmd validate pack/assets/slashblade/combostate/piercing_pl.vmd
python -m tools.vmd validate pack/assets/slashblade/model/pa/player_motion.vmd
python -m tools.vmd remap input.vmd output.vmd 0 10 100 151
python -m tools.vmd merge joined.vmd clip1.vmd clip2.vmd
```

For extraction, use a destination interval of the same length; for offsets, shift both endpoints equally. Explicit keys at both boundaries are required for every bone. Frame rounding that collides is rejected. Optional nonbone sections round-trip, but cannot be retimed accidentally. Model/name encoding is CP932; positions, quaternions and all 64 interpolation bytes are preserved.

The Piercing generator is intentionally not based on either upstream modern binary. It rebuilds the modern 1–90 contract from source semantics: r32 `None` before modern activation, full r32 `Stinger` from frame 33, the old 20-tick reset clock converted to frame 63, then a delayed Noutou recovery. The six-tick Noutou swing reaches its final pose at frame 72, holds it through frame 77 because r32 enters Noutou with `LastActionTime = currentTime + 5`, and returns to neutral at frame 78. The player VMD contains only `classic_root`, matching the generated bone-only PMD adapter. See `docs/research/piercing-classic-interpretation.md`.

## Validation

Run `python -m unittest discover -s tests -v`, then `python scripts/build_pack.py`. The build first cleans generated staging state, then creates runtime files and validates them before and after packaging. Fixed ZIP timestamps and sorted records make repeated builds byte-identical. CI performs these steps and uploads the ZIP and SHA256 file.

Tests cover malformed VMDs, duplicate/colliding keys, nonbone tail preservation, curve-boundary refusals, generated PMD structure, deterministic output, frame coverage, reconstructed legacy-to-modern matrices, effect resource contracts, modern Classic Interpretation policy, timeout semantics, the independent Old Dream oracle, the first-person renderer ceiling, standby/carry classification, dedicated Piercing blade/player atlases and clean generated-pack staging. They do not run Minecraft or prove visual quality.

`dist/` and every generated entry under `pack/` other than `pack.mcmeta` are build outputs and are ignored by Git. No experimental upstream clone or downloaded binary is committed.
