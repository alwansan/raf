# T1 — authentic original Raft FFT sampled-image roles on CPU Vulkan

**Status:** Verified scoped positive result, [GitHub Actions 41939314440](https://github.com/alwansan/raf/actions/runs/41939314440). **Not an Android water fix.** Original Unity kernel names, IDs and device pixels remain unverified.

## Independent question / method
B18 authenticated original DXBC-to-SPIR-V descriptor identity for all 20 compiled programs; B48 verified original CSharp selector candidate pairs; A1 verified original vs generated HLSL two-pass numerical agreement. None tested whether swapping the *two sampled input image view roles* in a genuine original FFT dispatch changes computed output. T1 independently exercises this question with the published A1 two-pass CPU Vulkan host derived privately at runtime, never altering the A1 host or original data.

Read-only source: ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, restored three-part `Raft_Data/sharedassets0.assets` 115,978,112 B SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, ComputeShader pathID2456 SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`. Use original-only vkd3d translated SPIR-V with Mesa CPU Vulkan, two genuine serialized adjacent compiled candidates per pair, actual texture/image writes and synchronization, 1024×1024 `rgba32f` seed19; compare unswapped and first/second pass swapped reads without exposing pixel values. This is independent of any Unity `FindKernel` index.

## Verified result

| Compiled original candidate pair | Baseline vs swapped first-pass input | Baseline vs swapped second-pass input | Scope |
|---|---|---|---|
| 0/1 | Output changes | Output changes | CPU Vulkan positive |
| 8/9 | Output changes | Output changes | CPU Vulkan positive |

Total: six actual original **two-pass** Vulkan executions, 2/2 pairs sensitive to first input swap, 2/2 sensitive to second swap. Six source-free negative/control unit tests also pass. [Successful original run](https://github.com/alwansan/raf/actions/runs/41939314440) at code `ec6618e14ef6a26ba0d0dc925f3b17056d03721a`; only bounded numeric counts and booleans leave private process. The tested bank0 image descriptors cannot be swapped while preserving original output for this controlled input. This is not full FFT mathematical equivalence or proof of authoring shader source / Unity runtime identity.

## Retained failures / rejected assumptions

- [Run 41938039589](https://github.com/alwansan/raf/actions/runs/41938039589): initial T1 strict C++ source-anchor whitespace mismatch, before private source; corrected. [Run 41938194915](https://github.com/alwansan/raf/actions/runs/41938194915) first reached original but failed `-11` without pair diagnostic.
- [Run 41938536760](https://github.com/alwansan/raf/actions/runs/41938536760) identified Mesa lavapipe `SIGSEGV/-11` specifically original candidate pair18/19 when second-pass sampled descriptors swapped; not a positive numeric result.
- [Run 41938860477](https://github.com/alwansan/raf/actions/runs/41938860477) proved bank1 further had a failed source-oracle completeness check; [run 41939082498](https://github.com/alwansan/raf/actions/runs/41939082498) localized pair10/11 second-swap comparator tolerance false, finite written output. Bank1 numeric conclusion stays **INCONCLUSIVE**. These failures are not evidence that actual Android kernel-index bug is fixed or that one resource name should be replaced.
- The final scoped run deliberately excludes unstable bank1 cases, with this limitation prominently retained; no duplicate identical risky experiment was repeated after diagnosis.

## Reproduction and next critical path

Run `python3 -m unittest discover -s tests -p test_t1_fft_binding_sensitivity.py -v`, then `python3 -m scripts.t1_fft_binding_sensitivity --source <SHA-verified sharedassets directory> --runner <isolated T1 C++ Vulkan host>`. The full pinned ZIP2 acquisition, compile and execute contract is in [the isolated T1 workflow](../.github/workflows/raft-t1-fft-binding-sensitivity.yml). No private shader bytes, original managed source, converted HLSL, SPIR-V modules or pixel arrays committed or uploaded.

**Next blocker:** original authorized `.compute` source and serialized CSharp/runtime Unity `ComputeShader` binding/20 candidate program identity are still missing, with Vulkan/Adreno capabilities and Unity 2021.3.45f2 import untested. Treat `WATER-001` OPEN and readiness **NOT_READY / 0/3**. Audio/Settings and deferred touch remain untouched.
