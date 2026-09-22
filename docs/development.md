# Development

Runtime output is a normal resource pack. Nothing under tools/, scripts/, tests/ or docs/ is shipped. Existing root MIT copyright is retained.

## Source refresh

Check out `0999312/SlashBlade_Resharped` at `6e2a0a092fb794d7ea56fd83452869674f3ab1c7`, then run:

```sh
python scripts/extract_frame_maps.py /path/to/SlashBlade_Resharped
```

The extractor resolves Builder defaults and explicit resource constants and fails if a registration is not parsed. It emits 43 player entries and 92 blade entries. The full source asset inventory is recorded separately; upstream assets are not build dependencies or copied into the pack.

Legacy constants are pinned in `data/legacy_motion_map.json`, from the 34 ComboSequence definitions. Frame plan and approximation labels are in `data/bake_slots.json`. A build needs no network access or proprietary binary inputs.

To re-extract those constants, run `python scripts/extract_legacy_map.py /path/to/pinned-legacy-source`. It parses numeric expressions without executing Java or arbitrary Python input.

The first-person renderer contract is pinned separately in `data/first_person_render_contract.json`. It records the r32 `FPVOldStryleLike` matrix, Projectile Barrier branch, the pinned Resharped first-person matrix and the resource-pack capability classification. See `docs/research/first-person-rendering.md`. Because the modern renderer resets the incoming `PoseStack` to identity, item-model `firstperson_*` display transforms are not a valid override path for the pinned target; do not add such a file and claim FPV restoration without a source change that makes the assumption true.

## VMD tooling

```sh
python -m tools.vmd inspect pack/assets/slashblade/combostate/motion.vmd
python -m tools.vmd validate pack/assets/slashblade/model/pa/player_motion.vmd
python -m tools.vmd remap input.vmd output.vmd 0 10 100 151
python -m tools.vmd merge joined.vmd clip1.vmd clip2.vmd
```

For extraction, use a destination interval of the same length; for offsets, shift both endpoints equally. Explicit keys at both boundaries are required for every bone. Frame rounding that collides is rejected. Optional nonbone sections round-trip, but cannot be retimed accidentally. Model/name encoding is CP932; positions, quaternions and all 64 interpolation bytes are preserved.

## Validation

Run `python -m unittest discover -s tests -v`, then `python scripts/build_pack.py`. The build creates runtime files and validates them before and after packaging. Fixed ZIP timestamps and sorted records make repeated builds byte-identical. CI performs these steps and uploads the ZIP and SHA256 file.

Tests cover malformed VMDs, duplicate/colliding keys, nonbone tail preservation, curve-boundary refusals, generated PMD structure, deterministic output, frame coverage, reconstructed legacy-to-modern matrices, effect resource contracts, modern Classic Interpretation policy, timeout semantics, the independent Old Dream oracle, and the first-person renderer ceiling. They do not run Minecraft or prove visual quality.

Source-generated `pack/` VMDs/effect assets and metadata are tracked for inspection. `dist/` is a build output uploaded by CI. No experimental upstream clone or downloaded binary is committed.
