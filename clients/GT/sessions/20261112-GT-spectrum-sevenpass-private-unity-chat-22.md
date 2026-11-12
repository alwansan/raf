# GT — Chat-22: SHA-original Spectrum 7Pass → 28 Vulkan stages → 7 source states → 2 private ShaderLabs → Unity trial

**Date:** 2026-11-12. **Agent:** GT. **Only writable branch:** `feature/android-native-port`. **Read-only source:** `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`. No Git LFS. T1–T5 stopped by owner; preserve their evidence. No original .meta/GUID/scene/Material edits.

## Verified source and real CI evidence

- Original Shader: `UltimateWater/Spectrum/Water Spectrum`, B09 `sharedassets0.assets` 115,978,112 B SHA-verified source, PathID2432; one SubShader, **7 original Passes**, two keyword variants each, each VS+FS = **14 source VS/FS pairs / 28 stage references**. This is stronger than LogRaft's six-pass minimum (requested pass index #5).
- [First new workflow 43273060728](https://github.com/alwansan/raf/actions/runs/43273060728) **FAILED at B09 staging**: generic ZIP2 source stager wrote `Raft_Data/sharedassets0.assets`, while B09 expects flat `./sharedassets0.assets`; exact owner SHA/115,978,112 byte stage passed. Fixed by relocating only the authenticated runner-private staged copy, no ZIP2 edits, in commit `15e3f055`.
- [43273276394 SUCCESS](https://github.com/alwansan/raf/actions/runs/43273276394): 6 source-free tests, actual original owner staged privately, real paired VS/FS HLSL glslang Vulkan 1.1 + spirv-val **28/28** compiled, **13 distinct original program translations**. Output only sanitized safe numeric status; no ShaderLab, Unity, original sampler equivalence or phone pixel proof.
- [43273958426 SUCCESS](https://github.com/alwansan/raf/actions/runs/43273958426): 7 additional source-free state negative tests, source SHA pin, actual **7/7 separate render states**, **1,898 bytes** of private serialized ShaderLab states, **7 distinct state digests**, **6 original properties** (2 textures, 3 floats, 1 vector). Scratch-only original state text; no original values published.
- [43274729958 SUCCESS](https://github.com/alwansan/raf/actions/runs/43274729958): 7 additional private ShaderLab tests + 6 pair tests + 7 state tests, source-authenticated from ZIP2. Built **two private seven-pass ShaderLab candidates**, each selecting one of two original keyword variant permutations, **14 full Pass envelopes** / **28 stage references** / **7 source-authentic render states per candidate** / **6 source-authored properties**. Structural pass_coverage true. Important: **two isolated variants are NOT one authentic runtime keyword-routed ShaderLab**, don't merge as production.
- Actual source-safe scripts: `scripts/gt_spectrum_original_pair_compile.py`, `scripts/gt_spectrum_original_pass_states.py`, `scripts/gt_spectrum_original_private_seven_pass_shaderlab.py`. Workflow `.github/workflows/raft-gt-original-spectrum-seven-pass-paired-glslang.yml`; all original bytes remain scratch-only, never in artifacts. Tests in `tests/test_gt_spectrum_*.py`.

## New real Unity 2021 Android Vulkan isolated test

- Wrote `android-port/Experiments/GT/Editor/OriginalSpectrumSevenPassValidation.cs`: read-only relative to game project, imports ONE private Spectrum variant0, asserts 7 Passes, builds actual BuildTarget.Android Vulkan AssetBundle, reads shader error count and preserves only safe numbers. Does not touch original materials/Scenes/Meta, does not claim real keyword/CB0/sampler/RT or Adreno parity.
- `scripts/gt_spectrum_private_unity_project.py` stages disposable project `gt-private-spectrum-unity` inside checkout with one candidate, C# verifier, pinned Unity2021 project settings, no original .meta. Tested by `tests/test_gt_spectrum_private_unity_project.py`.
- [43275506146](https://github.com/alwansan/raf/actions/runs/43275506146) was **running actual Unity Editor Android Vulkan ShaderBundle build** when this checkpoint was first written. Do not mark success until Unity job and **safe report** `ProbeResults/gt-spectrum-sevenpass-unity-safe.json` are both checked. A failure is actionable, not proof of bad source game asset. The older full native [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) remains independent/active at last check and predates this change. Do not duplicate it.

## Honest remaining work / P06 milestone M2

1. Wait for / inspect real isolated Unity source variant0 job 43275506146; if failure extract first actual error and correct only source-justified translation (not fake sampler/keyword).
2. If variant0 Unity truly passes, validate variant1 and **both original variant-selection conditions** into one authentic 7Pass ShaderLab (original keyword flags/scope; no inferred selection).
3. Validate source-authentic register binding, CB0 properties, Texture/Sampler layout and render target lifetime, original GUID from same-instance AssetRipper exported Material. Then integrate proven shader into Native pipeline; no GUID hack.
4. Original Foam/Global still 2Pass missing Unity/phone proof; kernel index6 source identity unproven. 770 remaining postvendor custom Material docs are Dummy. CL phone invalid pass baseline 42,229 (Spectrum 19,191 / Foam 23,038), compute index6 7,263; source test successes do not erase old phone errors.
5. New full Android APK+OBB+XAPK must be generated from integrated verified changes and **tested on phone** for colours/water/fire/performance, fresh LogRaft strict gate and screenshots. Package CRC is not GPU proof.

## Recovery protocol

Read `clients/GT/RESTORE_AR.md`, `RESTORATION_PLAN_AR.md` and JSON, `state.json`, `SUMMARY_AR.md`, `MEMORY.md`, this file. Inspect newest Git HEAD, run 43275506146 and native 43247161671. Only write to `feature/android-native-port`. Do not use LFS. After each new proof, update plan P06 and M2, state, summary, memory, RESTORE, this session; link CI Run ID and say which proof levels remain **FALSE**.
