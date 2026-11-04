# B47 — Water ComputeShader source entrypoint guard (2026-11-04)

Session: `20261104T2055Z-B47-c4e7`; issue WATER-001.

## Actual change
Source fix [7453d67](https://github.com/alwansan/raf/commit/7453d673ee7758645f21dcffac5a5a77f87e6a4c) and correction [52e9b81](https://github.com/alwansan/raf/commit/52e9b812d5e77c0d0afb7a05b2334bb28cad281c) replace an unsafe source-candidate inference. Before the fix, a standalone `#pragma kernel FFT` without an HLSL entrypoint qualified as a water/FFT compute candidate. The added `scripts/b47_compute_kernel_contract.py` checks that each live pragma has exactly one corresponding `[numthreads(x,y,z)] void Kernel(...){...}` definition, with literal positive group dimensions, a product at most 1024, closing braces and unique names. The production `scripts/verify_water_render_contract.py` consumes this bounded profile and rejects symlink metas as valid source candidates.

## Proven checks
- [B47 CI 41912450062](https://github.com/alwansan/raf/actions/runs/41912450062) **COMPLETED SUCCESS** from immutable source `52e9b812d5e77c0d0afb7a05b2334bb28cad281c`. Eight new synthetic controls and five existing water-contract tests pass, Python syntax check passes.
- Negative controls reject bare pragma; comments/quoted fake pragmas; missing, mismatched, unfinished or duplicate kernel definitions; zero/oversized thread groups; duplicate names; and meta symlinks. Positive one- and two-kernel controls pass.
- [First CI 41912297055](https://github.com/alwansan/raf/actions/runs/41912297055) **FAILED** before test import because B47 accidentally inserted a literal escaped newline between two Python imports. Corrected and verified in `52e9b81`; **not** an original shader failure.
- B49 simultaneously delivered the ShaderLab *per-pass* fix at [5070247](https://github.com/alwansan/raf/commit/50702470954774ba96fe27509f1f9eddfd1aa4ea). B47 abandoned its competing patch and did not overwrite B49. B47's compute kernel work is separate.

## Evidence class and remaining blockers
This is **source-only structural integrity**, not a restored original ComputeShader and not runtime proof. Authenticated original ZIP2 kernel-index→compiled-program identity, original bytecode translation, Unity Android compilation, FFT numeric/pixel agreement and POCO device acceptance remain unverified. Macro-generated entrypoints may be conservative false negatives pending independent proof. No original asset/shader body or private data was published. `authentic_water_kernel_identity_verified` and `device_execution_verified` remain false, WATER-001 remains OPEN, game NOT_READY with 0/3 independent full reviews.

No audio, Settings, touch, original `.meta`/GUID, CL, full native build, Release, scheduled automation, other worker workflow or protected branch was modified.

Next: correlate original Unity serialized compute kernel index with the runtime `FindKernel/Dispatch` API and original compiled stage identity, then verify authentic restoration with independent Unity/GPU/device tests. Do not repeat the successful per-pass or synthetic kernel tests without a new hypothesis.
