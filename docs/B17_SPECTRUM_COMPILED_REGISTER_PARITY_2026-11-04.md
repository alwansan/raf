# B17 — Spectrum compiled resource registers (2026-11-04)

Session: `20261104T2249Z-B17-cbind` · Issue: `WATER-001`

**Source-authenticated PASS:** [CI 41930225633](https://github.com/alwansan/raf/actions/runs/41930225633), both synthetic and original jobs successful. Synthetic parser tests **17/17**; authentic original Spectrum **7 passes, 14 matched permutations, 28 stage-program instances**. Executable DXBC texture/sampler/UAV numeric resource registers match original Unity serialized per-stage resource indices. This is verified source metadata parity, not proof of shader semantics, compiled HLSL names, sampler state, Unity import, GPU pixels or Android playback.

Original provider: immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; `sharedassets0.assets` reconstructed from 3 parts, 115978112 bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. Aggregate-only CI artifact ID **13371811436** contains numeric evidence, no proprietary program or source bytes.

Implemented `scripts/b17_spectrum_compiled_bindings.py`, `tests/test_b17_spectrum_compiled_bindings.py` and `.github/workflows/raft-b17-spectrum-compiled-bindings.yml`. First authentic runs [41929705240](https://github.com/alwansan/raf/actions/runs/41929705240) and [41929877074](https://github.com/alwansan/raf/actions/runs/41929877074) failed closed; [41930060613](https://github.com/alwansan/raf/actions/runs/41930060613) classified the unsupported original sampler table as `UNITY_SAMPLER_TABLE`. Reusing B17's independently authenticated serializer-table aliases resolved the rejection without replacing any game resources.

Next: B09's distinct Spectrum HLSL/ShaderLab work can consume this numeric gate; requires independent source→generated program and sampler-name/binding verification, pass and keyword/state fidelity, real Unity import and Adreno pixel/device evidence. Original water rendering in APK86 remains broken. `WATER-001` OPEN; game NOT_READY 0/3. No game shaders, materials, audio, Settings, touch, .meta/GUID, native build, release or protected branches altered.
