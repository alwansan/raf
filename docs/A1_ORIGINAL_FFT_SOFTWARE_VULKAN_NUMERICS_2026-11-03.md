# A1 — executable original FFT versus HLSL roundtrip on CPU software Vulkan

**Date:** 3 November 2026. **Branch:** `feature/android-native-port`. **Client:** `raft-20261103T145000Z-a1c92f74`. **Final verified source SHA:** [3406dd121ebeca30ad344ccd8f71278fe0505310](https://github.com/alwansan/raf/commit/3406dd121ebeca30ad344ccd8f71278fe0505310).

## What this actually executes

Unlike earlier SPIR-V opcode/SSA histograms, this A1 experiment runs executable original FFT compute programs: SHA-authenticated original DXBC → VKD3D SPIR-V, and the same translated SPIR-V → SPIRV-Cross HLSL 5.0 → glslang SPIR-V. Both variants are dispatched independently through **Mesa lavapipe CPU Vulkan 1.1**, sharing identical deterministic host-initialized input images. Descriptor set 0 provides two separately sampled images at bindings 0/1 and one output storage image at binding 2. Each output goes to a separate sentinel-initialized backing image, so even empty writes cannot be counted as agreement.

- Backing images: **linear-tiling `VK_FORMAT_R32G32B32A32_SFLOAT`**, fixed 1024×1024, host-coherent memory. This tests one legitimate RGBA32Float-class image view, **not** the whole original RGHalf/RGFloat/ARGBHalf/ARGBFloat cache matrix.
- Device requirements are checked explicitly: software **CPU** physicalDeviceType (no GPU fallback), sampled+storage format support, and `shaderStorageImageWriteWithoutFormat`. Vulkan pipeline or descriptor failures are errors, not silent skips.
- Dispatch per original variant's actual local workgroup shape at (groupX=1, groupY=1 or 2). Original source program variants span X=64,128,256,512,1024; the positions are **compiled variant slots**, not proved Unity runtime kernel indices.
- Three distinct workload scenarios, `(seed=0,Ygroups=1)`, `(seed=19,Ygroups=1)`, `(seed=257,Ygroups=2)`. A1 compares only pixels actually written and verifies identical write coverage, finite values, maximum absolute and relative L2 differences.
- All original DXBC/HLSL/SPIR-V and image values remain inside CI temporary directories. Logs contain **only** numeric aggregates and per-slot comparison metrics. No binary or reconstructed shader artifact is uploaded.

## Verified control and original results

[Initial canary source run 41658674936](https://github.com/alwansan/raf/actions/runs/41658674936) **SUCCESS**: synthetic separate-texture GLSL compute adds two source texels, returns eight correct written pixels and zero numeric difference in positive comparison. Intentional `a-b` negative control produces `max_abs_difference=0.874038696289`, `relative_l2_difference=1.01384076937`, and `within_selected_tolerance=false`. This validates actual software Vulkan image read/write and detects real arithmetic differences, not just SPIR-V validation.

[First authenticated20 original run 41659199363](https://github.com/alwansan/raf/actions/runs/41659199363) **SUCCESS**: 20/20 SHA-authenticated original compiled variants executed versus their independently generated HLSL roundtrips with exactly matching written pixel values in the initial workload. Zero inconclusive cases.

**Final extended experiment:** [GitHub Actions 41660159285](https://github.com/alwansan/raf/actions/runs/41660159285) **COMPLETED SUCCESS**, synthetic job **126000930338**, authenticated original job **126001151314**, exact source `3406dd121ebeca30ad344ccd8f71278fe0505310`. All **8/8** schema and negative-control tests passed on both jobs. SHA verification checked *exactly one* original LFS payload `sharedassets0.assets`: **115,978,112 bytes**, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`. FFT owner `pathID=2456` raw-object SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`; verified original DXBC SHA hashes per 20 programs.

| Evidence | Result |
|---|---:|
| Original compiled FFT programs | 20/20 |
| Authenticated software Vulkan executable pairs | 20/20 |
| Executions per program | 3 |
| Total authentic original-versus-roundtrip comparisons | **60/60** |
| Cases with the same written-pixel coverage and numerical output | **60/60** |
| Any inconclusive/program failure | **0** |
| Maximum absolute pixel component difference | **0** |
| Maximum relative L2 difference | **0** |
| Two-Y-group original written-pixel range | **128–2048** |
| Observed Android/Adreno/Unity execution | **none** |

## Significance, limits and next work

Previously A1 proved arithmetic opcode profiles and SSA producer-edge profiles **0/20** identical after HLSL roundtrip, and public GLSL.std.450 opcode histograms **20/20** identical. This **executable 60-case numerical comparison** demonstrates that structural opcode/SSA changes did **not** alter the outputs of these selected valid Vulkan RGBA32F workloads. Similarly, the original storage-image `Unknown` versus roundtrip `Rgba32f` typed image declaration mismatch did not prevent these two shaders from producing identical values when both were bound to RGBA32F software Vulkan image views.

**Not proven:** numerical equality for *all* input arrays, complete two-pass water FFT, other input/output image formats (especially RGHalf/ARGBHalf and RGFloat), half/float precision policy, shader variant/runtime kernel selection under Unity, resource lifetime, full authored ShaderLab integration, Adreno Vulkan feature support, game rendering or installed Android visuals. A CPU software-Vulkan result is *not* an Android GPU result. Authentic water resource contract remains false, and no arbitrary field/index/kernel is patched to pretend it is true.

Initial synthetic failure [41658505014](https://github.com/alwansan/raf/actions/runs/41658505014) required the public samplerless-texture GLSL extension; subsequent intermediate source/test-integration runs exposed a test-metadata mismatch and C++ declaration ordering, repaired before the final exact-source successes. These are experiment engineering fixes, not Raft gameplay defects.

No original game assets, shaders, `.meta`/GUIDs, `.rgd`, left Mouse0/500ms/UGUI/Xbox, W1 graphics pass recovery, signed delivery, native request, protected branches, CL or scheduled tasks were modified. Only independent CPU software Vulkan tester, its private CLI and CI tests were added. Last installed game APK80 from source `9462f8e` does not contain these experiments. **WATER-001, RENDER-002, FFT-FORMAT-009 remain OPEN; NOT_READY, readiness full independent same-SHA reviews 0/3.**

**Next focused step:** test the authenticated original channel/precision matrix with **actual RGHalf, RGFloat and ARGBHalf storage/view formats** and restore their Unity binding contracts before installing any reconstructed shader; keep W1's pass reconstruction work independent.
