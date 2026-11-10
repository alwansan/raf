# 20261110-GFX-chat-spv-index-memory-writer-47 — GFX-MULTI-074

- origin=chat; role=GFX-LAB; branch=`experiment/android-graphics-rootcause` only
- resumed_from: `GFX-MULTI-073` [CI42890357390](https://github.com/alwansan/raf/actions/runs/42890357390) SUCCESS, 530 unit tests, 427/427 private b/register+literal index-shape multiset equality.
- base_sha (before this chat's writes): `27522f41c7bd68e7b4c564969f418472177dc6cb`
- experiment_key: `GFX-MULTI-074`
- source_ref: ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- scope: source-private, authenticated SPV real UBO dynamic index `OpBitcast(OpLoad)` and `OpIAdd(literal,OpBitcast(OpLoad))` tracing to conservative same-block `OpStore` local writer candidate and bounded stored-value `OpShiftLeftLogical` SSA ancestry. No game APK, no T1–T5 edits.
- control: synthetic positive and negative cases for branch and label boundaries, function call, unknown alias, non-standard memory operands, no store, pure value without shift, duplicate loads, invalid original UBO layout, untrusted OpSelect dynamic index.
- code: `gfxlab/tools/multi_shader_spv_index_memory_writer074.py`; `gfxlab/tools/multi_shader_original_cb_index_private_multiset074.py`; `gfxlab/tests/test_multi_shader_spv_index_memory_writer074.py`.
- workflow: `.github/workflows/gfxlab-multi074-SPV-dynamic-CB-index-memory-writer.yml`
- runs: **pending**. Verify exact GFX074 workflow run and final success/failure; do not infer CI completion from a committed file.
- outcome: **NOT_VERIFIED** at initial session commit.
- evidence_level: `PENDING_ORIGINAL_SOURCE_AND_TRANSLATED_SPV_CPU`. Source SHA, 157 original pairs, 314 stages, 311 with CB and 427 dynamic reads are mandatory invariant checks during CI, not new proven results before run.
- limitations: A local same-block SPV store is only a bounded **candidate**, not whole-CFG dominance or absence of pointer alias; neither a source original DXBC temp register/component→SPV index SSA identity nor numeric value equality. Original Material property→DXBC register/CB byte semantics remain GFX054 blocked. Original Shader48 Android GPU, PC↔Adreno pixel parity and owner acceptance remain FALSE.
- negative claims: `originalShaderRestored=false`, `phase_closed=false`.
- next: inspect CI logs/artifact/purge and any failure, fix only in this branch, update this session and all five persistent restore files. Then consider narrower source DXBC def-use and SPV memory SSA/CFG proof (GFX075) only after current gate is validated.

### GFX074 CI availability check — 2026-11-10T20:27:12Z UTC
GitHub Actions latest branch runs endpoint still lists GFX073 CI42890357390 as newest, with NO GFX074 run visible. Thus code and YAML commits exist but GFX074 real/source-free test result is **NOT_VERIFIED; run_id=null** (not a test failure). Use GitHub Actions workflow_dispatch for `.github/workflows/gfxlab-multi074-SPV-dynamic-CB-index-memory-writer.yml` on `experiment/android-graphics-rootcause`, or wait for a genuine new Actions run event, then inspect its result. Never fabricate a CI run number.
