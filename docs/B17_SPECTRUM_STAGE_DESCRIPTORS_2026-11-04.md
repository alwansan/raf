# B17 — authenticated original Water Spectrum stage resource table contract
**Date:** 2026-11-04 UTC  
**Issue:** WATER-001 (P0) · **Agent:** B17 · **Session:** `20261104T2140Z-B17-spc2` · **Scoped outcome:** SOURCE_VERIFIED, NOT_RUNTIME_VERIFIED.

## Execution and reproducible evidence

[Final workflow 41920232173](https://github.com/alwansan/raf/actions/runs/41920232173), source [6afb4e1280f6691e3b47ac810f479409f94a9e58](https://github.com/alwansan/raf/commit/6afb4e1280f6691e3b47ac810f479409f94a9e58): **COMPLETED SUCCESS**. Synthetic job: **16/16 tests PASS** (normal stage descriptors, negative malformed/unsafe schemas, bool-as-index rejection, serialized boolean type distinction, mutation-sensitive resource signatures). Real-original job: **SUCCESS**; it reassembled 3 ZIP2 Git parts, authenticated 115,978,112 exact bytes with SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, then executed a UnityPy 1.25.4 original serialized Shader read. ZIP2 source pin: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. No LFS. [Aggregate-only CI artifact](https://github.com/alwansan/raf/actions/runs/41920232173) named `b17-spectrum-numeric-contract-41920232173`, artifact ID `13367106561`; seven source pass signatures are retained there without raw shader names/bytes.

The probe additionally *reuses* W2's independently established authentic original **one-subshader, seven-pass, original vertex/fragment variant-and-constant-buffer topology** assertions before collecting stage resource descriptors. Result: **7/7 original passes** structurally inspected, **13 fragment-stage descriptor records** and **0 vertex-stage descriptor records**, **42 observed resource-table field occurrences** across the fourteen stage records. This is precise serialized descriptor metadata, not runtime texture bindings, authored ShaderLab or pixel equivalence.

Source-specific schema facts: actual Unity serialization uses `m_UAVParams` (not only the initially guessed `m_UAVParameters` alias); the texture parameter `m_MultiSampled` is an actual Boolean. The final parser preserves that bool's type in its digest and still rejects bool substitution for numeric slots/indices. Digests cover serialized numeric descriptor rows and typed bools, not proprietary names, raw original source or binary shader programs.

## Failure history and rejected hypotheses

- [41919077512](https://github.com/alwansan/raf/actions/runs/41919077512): synthetic PASS and ZIP2 payload SHA verified; authentic extraction returned a `ValueError`. Did not publish arbitrary exception content.
- [41919278787](https://github.com/alwansan/raf/actions/runs/41919278787): safe failure class identified a missing whitelist schema alias.
- [41919556812](https://github.com/alwansan/raf/actions/runs/41919556812): source safely exposed only the structural Unity field label `m_UAVParams`. Rejected the hypothesis that our initial name whitelist covered the original serialization.
- [41919713269](https://github.com/alwansan/raf/actions/runs/41919713269): source rejected a nonnumeric field, disproving “all descriptor fields are integers.” The public known-schema Boolean `m_MultiSampled` was implemented with exact typed controls.
- [41920193184](https://github.com/alwansan/raf/actions/runs/41920193184): first original+synthetic green (14 tests); [41920232173](https://github.com/alwansan/raf/actions/runs/41920232173) confirms **16/16** final tests and identical original 13/0 counts.

These earlier red runs are **expected fail-closed development experiments**, not evidence that game original content is damaged.

## Integration boundary and next engineering consumer

The reusable, *now source-verified* code is `scripts/b17_spectrum_stage_descriptors.py` with synthetic tests `tests/test_b17_spectrum_stage_descriptors.py` and isolated `.github/workflows/raft-b17-spectrum-descriptors.yml`. A future authentic Spectrum ShaderLab HLSL/SPIR-V translator can consume the seven per-stage numeric table fingerprints to reject missing/incorrectly bound texture/UAV/sampler records and verify stage/pass identity against the same pinned original — **only after** establishing actual compiled program and resource-to-authored-wrapper lineage. Do **not** infer semantics solely from equal row counts or arbitrary equivalence of name hashes; record original sampler mode, texture type, sRGB, constant-buffer offsets and binding slot contracts, plus numeric/pixel and Unity/Adreno proofs. A different original source SHA or unknown table schema must fail closed, never auto-fill dummy resources.

This work **does not** restore/modify the Spectrum shader, compute FFT kernels, water materials, Unity project, shaders or resources; no original `.meta` GUIDs or `.rgd` files were changed. No native/Unity/APK build or device test was initiated. Owner-confirmed sound and Settings preserved; touch deferred. **WATER-001/RENDER-002/LOCAL-005 remain OPEN, game NOT_READY and full independent readiness reviews 0/3**. Released test APK86 remains older than this source-only result.
