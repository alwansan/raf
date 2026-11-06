# T1 — Unity 2021 source-free real GPU variant keyword experiment

- session_id: 20261106T171240Z-T1-chat-unity-keyword-runtime-9f3a
- origin: chat
- status: completed (scoped actual Unity 2021 sourcefree GPU variant test; NOT WATER-001 closure)
- issue_id: WATER-001 OPEN / NOT_READY 0/3
- base_sha: b6c03cc3f4c7d40444eca623e058bd67377b5d0b
- resumed_from_sessions: 20261106T170532Z-T1-chat-variant-declarations-7c4e; 20261106T163310Z-T1-chat-real-fft-pair-d91e; 20261105T140300Z-T1-chat-vulkan-editor
- work: prompt/coordination/work/WATER-001/20261106T171240Z-T1-chat-unity-keyword-runtime-9f3a.json
- experiment: prompt/coordination/experiments/T1/20261106T171240Z-T1-chat-unity-keyword-runtime-9f3a.json
- event: prompt/coordination/B_TEAM/events/T1/20261106T171240Z-T1-chat-unity-keyword-runtime-9f3a.json
- source owner pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 **not opened**
- active run: https://github.com/alwansan/raf/actions/runs/42259968584
- job_id: 128037003200
- published source sha: fa24a4479cce0d4275b5402947357b3b345f22af (synthetic compute)
- published test sha: fdbaa97641bee6746286ebef150c9449fd985950 (Unity C# NUnit)
- published source-only tests sha: 995b9000d4d7472686083f11c8a67ce4e9847581
- published workflow sha: b958990243523d18a6d44d888e6328e17fe07ddf

## Why this scope

Last T1 synthetic Python-only source validation [42258825614](https://github.com/alwansan/raf/actions/runs/42258825614) passed 11/11, checking keyword declarations and selector exclusivity; the new Unity `ComputeShader.IsKeywordEnabled` C# path was *not actually compiled/run*. Unity 2021.3 API confirms `EnableKeyword(string)` is a no-op for undeclared local keyword. Original SPIR-V vs HLSL numerics [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) match on same Mesa Vulkan inputs and 384 keyed reads; actual derived Unity/OpenGLCore reference still differs 63/64 pass0 and 31/32 pass1, so matched Vulkan fixture alone is not device water proof.

This new isolated public synthetic control does not modify private original FFT scripts, Unity original assets, or any other agent's files. No active T1 counterpart owning the four new files was found. Unity heavy shared concurrency group `raft-native-engine-${{ github.ref }}` cancel-in-progress:false; separate workflow path trigger only. SHA-pinned GameCI v0.1.72 and Unity2021.3.45f2, same known-positive GameCI fixture as previous T1 RGBA32F control. Both edit-mode NUnit tests must actually run and pass, including the 64 GPU outputs for default, enabled and disabled-again variants (192 uint32 results). Extra/missing/failed tests rejected by strict XML gate. Logs and project erased from runner. No private original source or game asset checkout.

## Current observed CI stage

Run https://github.com/alwansan/raf/actions/runs/42259968584 queued and started at 2026-11-06T17:15:30Z. Source-only fixture checks SUCCESS, pinned CLI extraction SUCCESS, license/disk preflight SUCCESS; as of checkpoint actual licensed Unity EditMode step in_progress. This is **not yet** GPU proof. Do not run another equivalent Unity workflow while active or cancel it.

## Strict follow-up

Read terminal status, job steps and bounded `RAFT_T1_KEYWORD_RUNTIME` marker. If success require both exact NUnit cases PASS and 3x64 GPU word assertions inside the test, then update own session/experiment/work/event. If fails, safely categorize source or GameCI stage; do not expose secrets/raw log or declare original water fixed. Any further actual Unity-vs-Vulkan original parity must use new independent source-authenticated fixture and should preserve previous actual OpenGLCore negative as a baseline.

WATER-001 OPEN / NOT_READY; no game APK/OBB/XAPK or Adreno evidence in this experiment.

## Terminal actual Unity result — 2026-11-06T17:17:30Z

- [GitHub Actions 42259968584](https://github.com/alwansan/raf/actions/runs/42259968584), job **128037003200**, terminal **SUCCESS**, source `b958990243523d18a6d44d888e6328e17fe07ddf`; license, checkout, all 6 source-free Python tests (2 direct fixture + 4 staging), SHA-pinned GameCI CLI, *actual Unity EditMode tests*, and cleanup all passed.
- Safe marker: `RAFT_T1_KEYWORD_RUNTIME` `unity2021_synthetic_nunit_passed=True`, `expected_tests=2`, `actual_tests=2`, `original_source_used=False`, `android_adreno_water_proven=False`. The strict NUnit parser checked exact method identities:
  `T1FftKeywordVariantRuntimeTests.UndeclaredComputeKeywordCannotBeEnabled` and `T1FftKeywordVariantRuntimeTests.DeclaredComputeVariantsProduceDistinctGpuWords`.
- Test code runs `ComputeShader.IsKeywordEnabled` for absent keyword and actual local declared keyword, and performs 3 real GPU `Dispatch(1,1,1)`+ComputeBuffer readbacks, each with 64 asserted uint32 entries (default `7+i`, enabled `29+i`, disabled `7+i`) = **192 words validated**. Both exact tests passed.
- This **independently verifies runtime API activation and synthetic compute variant execution in Unity 2021 Editor**. It is not a direct execution/compilation of the earlier full `android-port/Editor/T1FftKernelRuntimeProbe.cs` 20-row tool and does not prove variant mapping/source of original Raft FFT. No original `.compute`, DXBC or managed asset imported; no APK/OBB/XAPK, no Adreno or mobile graphics.
- Private GameCI logs, synthetic project and XML were deleted by confirmed successful cleanup; no release or artifact uploaded. No peer jobs cancelled. Source-free checks cannot explain the genuine Unity/OpenGLCore-vs-Vulkan FFT mismatch yet.
- **Next**: The authored FFT (original compiled slots -> Unity runtime kernel names + keyword configurations, resource bindings and dispatch sizes) must be source-authenticated, then tested on actual Unity GPUs and Adreno. Prior original SPIR-V vs HLSL same Mesa Vulkan numeric comparison [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) matched all 384 keyed reads; the Unity/OpenGLCore mismatch remains a separate unsolved issue, and forced Vulkan Unity startup had previously failed. Prefer independent source-controlled OpenGL integer/bitcast address lowering diagnostic rather than altering verified original HLSL blindly.
- **Session completed / resource released**, WATER-001 OPEN / NOT_READY 0/3.
