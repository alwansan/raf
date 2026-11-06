# T2 → T5 | next owner-authorized native Unity export: exact Foam private original 2-pass integration handoff

- **From:** T2, `20261106T2020Z-T2-chat-foam-export-guid-material-3c5e`, `origin=chat`; **to:** T5 (native integration coordinator); **issue:** WATER-001.
- **Immediate real-data gap:** owner-direct full run [42281310905](https://github.com/alwansan/raf/actions/runs/42281310905) at **older SHA `d6924001`** exported `UltimateWater/Foam/Global` with `original_meta_present=true` but **1** Pass against **2** required by device. The run stopped at an unrelated C# Editor physical mouse CS0234 compile error, not missing Foam. T4 owns the Editor fix; source-only T4 CI does not prove full Unity compile.
- **Our verified sources:** [code 0d0a9790](https://github.com/alwansan/raf/commit/0d0a9790b78953c6f7c7b6be1324a15dfd862bf2), [synthetic 16+17 CI42288126476](https://github.com/alwansan/raf/actions/runs/42288126476), **SHA-original private candidate + synthetic Material pointer CI42288126264 SUCCESS**. Original `sharedassets0.assets` byte-authenticated (115978112B), private 9731B original two-pass ShaderLab, old synthetic exported 1 → new synthetic 2 Passes, `.meta` and material YAML bytes unchanged, exact one synthetic `{fileID:4800000,guid,type:3}` link preserved. No source/GUID leaks or actual Unity runtime claims.
- **Scheduled T2 independent protection:** [014d48fa](https://github.com/alwansan/raf/commit/014d48fafbfd93b0bf0f2bff46c3c82ad2940ef3) / [CI42287347419](https://github.com/alwansan/raf/actions/runs/42287347419) blocks `.meta` GUID collisions before install. Chat T2's read-only `scripts.t2_foam_export_binding_probe` additionally checks all Assets meta and serialized Material pointers.

## Suggested insertion point and source-only validation (T5 owns shared YAML)

Only on a separately permitted **real native** workflow, after the original ZIP2 source `$RUNNER_TEMP/w1-original/Raft_Data/sharedassets0.assets` has been staged and SHA verified, all required tools (`vkd3d-compiler`, `glslang-tools` if used) are installed, and the transient `$RUNNER_TEMP/project/ExportedProject` exists. Insert an independently gated T2 Foam staging step **after W1 Depth Copy and B45 Blur recovery, but before the prebuild water contract**. Avoid modifying an already-running workflow/candidate.

The exact source root for T2's scripts is `$RUNNER_TEMP/w1-original` (parent of `Raft_Data`), unlike B45's `--source "$RUNNER_TEMP/w1-original/Raft_Data"`. Proposed commands, after verifying the existing runner can satisfy their scratch/disk budgets:

```bash
set -euo pipefail
mkdir -p "$RUNNER_TEMP/t2-foam"
python3 -m scripts.b20_private_foam_packet \
  --source "$RUNNER_TEMP/w1-original" --repo "$GITHUB_WORKSPACE" \
  --private "$RUNNER_TEMP/t2-foam/packet" \
  --out "$RUNNER_TEMP/t2-foam/manifest-safe.json"
python3 -m scripts.t2_foam_private_shaderlab_candidate \
  --source "$RUNNER_TEMP/w1-original" \
  --packet "$RUNNER_TEMP/t2-foam/packet" \
  --manifest "$RUNNER_TEMP/t2-foam/manifest-safe.json" \
  --private-dest "$RUNNER_TEMP/t2-foam/candidate.shader" \
  --out "$RUNNER_TEMP/t2-foam/stage-safe.json"
python3 -m scripts.t2_foam_export_binding_probe \
  --project "$RUNNER_TEMP/project/ExportedProject" \
  --out "$RUNNER_TEMP/t2-foam/actual-export-before-safe.json"
FOAM_SHA="$(sha256sum "$RUNNER_TEMP/t2-foam/candidate.shader" | cut -d' ' -f1)"
python3 -m scripts.t2_foam_private_installer \
  --project "$RUNNER_TEMP/project/ExportedProject" \
  --candidate "$RUNNER_TEMP/t2-foam/candidate.shader" \
  --source-stage-report "$RUNNER_TEMP/t2-foam/stage-safe.json" \
  --expected-candidate-sha256 "$FOAM_SHA" \
  --backup "$RUNNER_TEMP/t2-foam-original-export-backup" \
  --out "$RUNNER_TEMP/t2-foam/installed-safe.json"
python3 -m scripts.t2_foam_export_binding_probe \
  --project "$RUNNER_TEMP/project/ExportedProject" \
  --out "$RUNNER_TEMP/t2-foam/actual-export-after-safe.json"
```

The stage functions fail closed on missing source bytes or original identities. An observed `material_docs_referencing_exported_Foam_guid=0` is *permitted* (compiled original CIL uses `Shader.Find` and constructs the Material dynamically); do **not** manufacture a serialized link, fake a GUID or insert fallback shader aliases. Compare the read-only before/after count of Materials and exact Foam link counts and assert **after** `foam_exported_subshader_pass_counts == [2]` with all programs and `foam_exported_has_dummy_export_marker=false`; require byte-exact `.meta` backup identity and original source SHA proof, not just a guessed shader name. A before `[1]` is the current proven older native state but should be **rechecked** on the actual new export and not hard-coded if another worker already repaired Foam. Preserve pre/post aggregate JSON separately, never upload raw candidate/private packet, backup, source/game YAML, original shader/GUID or full Unity project; erase scratch via `if: always()` even if a gate later fails. Independent installed source proof is **not** a declaration of successful Unity 2021 Shader importer or Vulkan/Adreno pixels.

**Critical T5 trial integration:** applying a genuine Foam 2-pass candidate may change which precise water conditions are unmet. Recompute `verify_water_render_contract.inspect` and `record_documented_water_limitation` against that candidate, and reconcile the actual authorized native request's **exact** unmet-conditions list; do not silently bypass strict kernel/Spectrum/Depth gates or treat the prior request as permission for a different candidate. T5 determines if/when to request owner-supported build. No new Unity job dispatched by T2.

**Still unknown:** original compiled Material live binding, runtime `Shader.Find` resolution, CB0 offset/type/value uploads and samplers, original Spectrum/FFT, actual Unity import and any phone pixels. Further verification belongs to real transient export+Unity+phone; source-only confirmation of [1]→[2] synthetic transition cannot close WATER-001.
