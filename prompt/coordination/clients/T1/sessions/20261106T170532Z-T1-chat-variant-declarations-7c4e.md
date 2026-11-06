# T1 source-authored Unity FFT keyword-set and activation guard

- session_id: 20261106T170532Z-T1-chat-variant-declarations-7c4e
- origin: chat
- status: completed (source-only guard, not WATER-001 closure)
- issue_id: WATER-001 OPEN / NOT_READY 0/3
- base_sha: 67f20cf7fe5ae8619f4f084348333a9b81f6c2fe
- resumed_from_sessions: 20261106T163833Z-T1-chat-selector-alias-5e8b; 20261106T163310Z-T1-chat-real-fft-pair-d91e; 20261105T140300Z-T1-chat-vulkan-editor
- source owner: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 (not accessed in this scope)
- work: prompt/coordination/work/WATER-001/20261106T170532Z-T1-chat-variant-declarations-7c4e.json
- experiment: prompt/coordination/experiments/T1/20261106T170532Z-T1-chat-variant-declarations-7c4e.json
- event: prompt/coordination/B_TEAM/events/T1/20261106T170532Z-T1-chat-variant-declarations-7c4e.json
- verified source-only run: https://github.com/alwansan/raf/actions/runs/42258825614 (job 128033110287; completed SUCCESS)
- completed_at_utc: 2026-11-06T17:09:06Z

## New verified FFT evidence before this scope

The concurrently running earlier T1 authenticated original-vs-HLSL keyed GPU experiment https://github.com/alwansan/raf/actions/runs/42254539826 ended SUCCESS (job 128018118519, SHA fe3cff4899a19b197b64d692a28b2fdaf980fb7f). Original direct original-SPIR-V and translated HLSL ran with same actual source/butterfly GPU input bytes + dispatch manifest, had two distinct SHA-bound traces each [64,256,64], zero mismatched fetch coordinates/values across 384 matched invocation-keyed reads, and both Vulkan pass outputs numerically matched for this one 1024×32/seed19/one-group fixture. The standalone T1 pair-session work was still marked active and its session waiting_ci when read; **do not overwrite that session**. This result supersedes the earlier uncertainty about whether that *specific Vulkan fixture* could be numerically paired. It does NOT supersede authentic Unity/OpenGLCore negative [42025620147](https://github.com/alwansan/raf/actions/runs/42025620147) (63/64 and31/32 pass mismatches), Unity graphics backend drift, Android/Adreno/device water failures or original Unity runtime kernel identity.

## Independent scoped engineering fix

The previous nominal selector-alias fix [42255094227](https://github.com/alwansan/raf/actions/runs/42255094227) rejected duplicated named-kernel+keyword combinations, but staging still accepted different arbitrary/undefined keyword strings in each selector: Unity can ignore keywords not present in its imported shader keyword space. Unity 2021.3 documents per-compute shader keywords through `#pragma multi_compile(_local)`, `shader_feature(_local)` and ComputeShader.EnableKeyword/IsKeywordEnabled. This scope adds a necessary source-stage and runtime keyword guard, *not* actual author runtime-variant identity.

- `scripts/t1_stage_unity_fft_kernel_probe.py` commit [5a9f925](https://github.com/alwansan/raf/commit/5a9f925afdb01ca90167c5acc858a90a395a27fc): parse bounded explicit **active/uncommented** variant keyword pragmas; reject unsupported/macro-expanded pragma families, duplicate declared keyword names across sets, duplicate set alternatives, undeclared manifest keywords and multiple mutually exclusive keywords selected together. If a set has no explicit `_` or `__` default, require one selected keyword per row. Preserve original 20 compiled-slot/2 named-kernel mapping and fail-closed source/sha gates.
- `tests/test_t1_stage_unity_fft_kernel_probe.py` commit [479b168](https://github.com/alwansan/raf/commit/479b16853bb537f469b78cc1386f2eeb79476b84): add positive local default selection plus rejected fabricated/unknown keywords, mutually exclusive pairs, missing required keyword groups, commented-out declarations, single/duplicate/unsupported pragma alternatives.
- `android-port/Editor/T1FftKernelRuntimeProbe.cs` commit [ec89ec0](https://github.com/alwansan/raf/commit/ec89ec09e590fbb6a3b2174acc7ccf2e1fa0f239): after `shader.EnableKeyword`, call `shader.IsKeywordEnabled` and reject ignored/non-enabled keyword, not just `FindKernel`/threadgroup match. It still logs no private source or keywords and does not assert native authored mapping.

## Test outcomes and boundaries

- Intermediate source-only [42258711224](https://github.com/alwansan/raf/actions/runs/42258711224) PASS on tool-change SHA, with old 8 synthetic tests.
- New full synthetic [42258787510](https://github.com/alwansan/raf/actions/runs/42258787510) PASS 11/11 tests including 3 new variant declaration controls.
- Final coherent source+test+C# [42258825614](https://github.com/alwansan/raf/actions/runs/42258825614) **COMPLETED SUCCESS** at exact `ec89ec09`, job 128033110287. Only source-only Python parsing and tests executed: no original assets, no actual C# Unity compilation/activation, no GPU dispatch or phone test. No other Actions cancelled.
- This guard prevents a false **source-level variant attribution**. It cannot prove that different keywords produce different compiled binaries, that the authored single .compute exists, that original dispatch uses these keywords, or that Android water has correct graphics.
- No edits to T1 private Vulkan trace scripts or workflows of concurrent scope, to T2–T5 work, game original assets, Android native request, audio/Settings/touch, or packaging.

## Next T1 engineering step

Use the newly proven one-fixture original-vs-HLSL **same-Vulkan parity** to focus on the remaining real Unity backend divergence: compare Unity OpenGLCore compute shader compiler variant with identical original-source input readback, per-invocation keyed capture and private first mismatch, or establish a genuinely running Vulkan Unity Editor before reusing original data. The forced Vulkan GameCI path previously failed in source-free run 42047391061, so do NOT assume CLI `-force-vulkan` alone works. Separately run an isolated synthetic Unity 2021 Editor test for the new `IsKeywordEnabled` guard if an authored original/verified fixture is available; source-only green != C# compilation. WATER-001 OPEN / NOT_READY 0/3.

