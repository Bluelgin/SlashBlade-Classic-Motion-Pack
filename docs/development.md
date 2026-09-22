# Development

Runtime output is a normal resource pack. Nothing under tools/, scripts/, tests/ or docs/ is shipped. Existing root MIT copyright is retained.

Phase one is **source-complete but not runtime-complete**. `data/phase_one_scope.json` is the machine-readable boundary: every visual subsystem must remain either implemented or explicitly terminally classified. `python scripts/audit_phase_one.py` is a CI gate and must not be bypassed by relabeling an unknown/TODO state as complete.

## Source refresh

Check out `0999312/SlashBlade_Resharped` at `6e2a0a092fb794d7ea56fd83452869674f3ab1c7`, then run:

```sh
python scripts/extract_frame_maps.py /path/to/SlashBlade_Resharped
```

The extractor resolves Builder defaults and explicit resource constants and fails if a registration is not parsed. It emits 43 player entries and 92 blade entries. The full source asset inventory is recorded separately; upstream assets are not build dependencies or copied into the pack.

Legacy constants are pinned in `data/legacy_motion_map.json`, from the 34 ComboSequence definitions. Frame plan and approximation labels are in `data/bake_slots.json`. A build needs no network access or proprietary binary inputs.

To re-extract those constants, run `python scripts/extract_legacy_map.py /path/to/pinned-legacy-source`. It parses numeric expressions without executing Java or arbitrary Python input.

Renderer/resource contracts that cannot be inferred from the VMD frame maps are pinned separately:

- `data/first_person_render_contract.json`: r32 FPV matrix/Barrier branch and Resharped's hard-coded FPV wrapper.
- `data/standby_carry_contract.json`: VMD-driven main-hand standby versus Java-driven back/offhand carry.
- `data/player_pose_adapter_contract.json`: missing-bone `return value0` passthrough behavior.
- `data/effect_resource_contract.json`: slash/Drive/Judgement effect asset boundaries.
- `data/modern_classic_policy.json`: modern-only/shared semantic interpretation policy.

Do not add an item-model `firstperson_*` override and claim FPV restoration on the pinned target: the modern renderer resets the incoming `PoseStack` to identity. Do not add global model offsets to fake FPV/back-carry corrections either; those changes leak into active/third-person/custom-blade contexts.

## VMD tooling

```sh
python -m tools.vmd inspect pack/assets/slashblade/combostate/motion.vmd
python -m tools.vmd validate pack/assets/slashblade/model/pa/player_motion.vmd
python -m tools.vmd remap input.vmd output.vmd 0 10 100 151
python -m tools.vmd merge joined.vmd clip1.vmd clip2.vmd
```

For extraction, use a destination interval of the same length; for offsets, shift both endpoints equally. Explicit keys at both boundaries are required for every bone. Frame rounding that collides is rejected. Optional nonbone sections round-trip, but cannot be retimed accidentally. Model/name encoding is CP932; positions, quaternions and all 64 interpolation bytes are preserved.

The player-pose adapter intentionally contains only `classic_root`. Adding real `body`, arm or leg bones changes Resharped's blend path and is not a neutral refactor. r32's Java swing-clock restart cannot be reproduced by resource assets; any future synthetic arm VMD must be treated as a new approximation and runtime-tested before replacing the passthrough design.

## Validation

Run the same source gates as CI:

```sh
python scripts/verify_old_dream_oracle.py
python scripts/audit_phase_one.py
python -m unittest discover -s tests -v
python scripts/build_pack.py
python scripts/validate_pack.py dist/SlashBlade-Classic-Motion-Pack-1.20.1-v0.1.0.zip
```

The build creates runtime files and validates them before and after packaging. Fixed ZIP timestamps and sorted records make repeated builds byte-identical. CI uploads the ZIP and SHA256 file.

Tests cover malformed VMDs, duplicate/colliding keys, nonbone tail preservation, curve-boundary refusals, generated PMD structure, deterministic output, frame coverage, reconstructed legacy-to-modern matrices, effect contracts, modern Classic Interpretation policy, timeout semantics, the independent Old Dream oracle, first-person/carry renderer ceilings and player-pose passthrough. They do not run Minecraft or prove visual quality.

`source_complete: true` must never be interpreted as `runtime_complete: true`. Runtime acceptance requires actual Minecraft observation using `docs/testing-checklist.md`; until then CI must keep `runtime_complete` false.

Source-generated `pack/` VMDs/effect assets and metadata are tracked for inspection. `dist/` is a build output uploaded by CI. No experimental upstream clone or downloaded binary is committed.