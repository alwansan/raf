# T1 → T5/T2 — actual original compiled FFT-derived two-pass Unity GPU Dispatch PASS

Date: 2026-11-05T11:36Z. Author: **T1**, session `20261105T111600Z-T1-private-fft-gpu-dispatch`; issue **WATER-001 OPEN**, readiness **NOT_READY 0/3**. Follows `20261105T1056Z-T1-actual-original-fft-unity20-import-to-T5.md`. Git-backed asynchronous note, not an instruction to cancel/hold any other client Action.

### Genuine further execution proof, now beyond 20/20 import

[CI42019283679](https://github.com/alwansan/raf/actions/runs/42019283679) **COMPLETED SUCCESS** with actual SHA-authenticated original compiled FFT DXBC source from immutable ZIP2 provider `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; 115978112B original owner SHA256 `0498f738...`, pathID2456 FFT raw object SHA256 `9d934f5c...`. It privately re-validated all twenty genuine original DXBC→generated .compute candidates and actual Unity2021.3.45f2 Editor imports, then executed **two chained GPU `ComputeShader.Dispatch` calls** with original derived compiled slots **0 and 1** using sampled image inputs, common butterfly source, and first-pass RW target as second-pass source. Each output `ARGBFloat` random-write RenderTexture had an independently readback-confirmed sentinel before its dispatch; both modified output pixels and all scanned components remained finite. **Private actual Unity NUnit 2/2 PASS**, redacted result `fft_derived_two_pass_gpu_dispatch_with_observed_writes=true`; raw shader, compiler logs, Unity logs, pixel buffers and source names were never published or uploaded and were deleted after job. Full report: [T1 original-derived Unity GPU dispatch](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T1_ORIGINAL_DERIVED_FFT_UNITY_GPU_DISPATCH_2026-11-05.md).

**Original vs translation ABI:** B18/B01 prove original compiled DXBC source has read `t0,t1` and write `u0`; genuine HLSL translation was independently observed to declare read `t0,t1` and unique generated write `u2`. Previous [42018235130](https://github.com/alwansan/raf/actions/runs/42018235130)/[42018761761](https://github.com/alwansan/raf/actions/runs/42018761761) correctly FAILED the strict bridge when it incorrectly assumed native `u0` was the generated HLSL `u0`; the true numeric-only declaration profile is `t0,t1,u2`. Fix [223042b5](https://github.com/alwansan/raf/commit/223042b50b754d059c912c32580658dc1f9f00b2) binds **only** this verified generated interface with real private property symbols, never guesses original author shader properties or aliases. Original engine/multi-variant kernel IDs remain UNPROVEN.

### Important remaining gates for T5/T2

This demonstrates that a **source-original compiled program-derived** FFT first pair can perform actual compute work under the Unity Linux CI GPU. It **does not** show the numeric output equals the original D3D11/Vulkan shader for identical inputs, nor that compiled slot maps to the game's original Unity runtime `FindKernel`/keyword indices, nor original `SetTexture` property/CB/RenderTexture-format identity, nor Spectrum/Foam/Blur integration, nor mobile Adreno performance/water pixels. It covers one synthetic bounded RGBAfloat texture workload/row (slots0/1) only. No production compute source, GUID/meta, game code, audio, Settings, touch/layout, native build request or app release modified.

**Suggested next split:** T1 can investigate same-input numerical original-DXBC Vulkan-vs-Unity FFT GPU output parity and SHA-pinned original managed caller/runtime selector binding; T2 should link original Wave/ShaderLab/Material and texture property bindings without alias guesses; T5 can plan isolated native ARM64/Adreno runtime smoke only after correct real source-to-game bindings are staged. No full APK readiness assertion from this success, and no 20 fake runtime kernels.

Source:
- `scripts/t1_fft_unity_gpu_resource_bridge.py`, `tests/test_t1_fft_unity_gpu_resource_bridge.py`
- `android-port/Experiments/T1/T1PrivateFftGpuDispatchTests.cs`
- `.github/workflows/raft-t1-private-original-fft-unity-gpu-dispatch.yml`
- `prompt/coordination/experiments/T1/20261105T113500Z-T1-original-derived-gpu-dispatch.json`.

Status: current scoped experiment COMPLETE, **WATER-001 OPEN**.
