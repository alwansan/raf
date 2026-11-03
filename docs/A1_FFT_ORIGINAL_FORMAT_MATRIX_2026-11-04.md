# A1 — Original Raft FFT four-format software Vulkan recovery

**Date:** 4 November 2026 (Asia/Baghdad). **Client:** `raft-20261103T224500Z-a1d7e439`. **Source:** [`34e7f04d8571eed231758cb7ba70a04e39643833`](https://github.com/alwansan/raf/commit/34e7f04d8571eed231758cb7ba70a04e39643833) on writable `feature/android-native-port`; original game source read-only `zip2` [`15964ea8f246b6e076ce26b60931ee2e1a9a2385`](https://github.com/alwansan/raf/tree/15964ea8f246b6e076ce26b60931ee2e1a9a2385/Raft).

## Engineering change (not only a diagnostic census)

Raft's authenticated original `GpuFFT.RetrieveRenderTexturesSet()` allocates temporary FFT textures according to original `_TwoChannels` and `_HighPrecision` flags: `RGHalf`, `RGFloat`, `ARGBHalf`, and `ARGBFloat`. Earlier A1 authentic FFT numerical execution tested just `ARGBFloat` / `VK_FORMAT_R32G32B32A32_SFLOAT`, so it could not establish real half precision or two-channel storage compatibility.

This session extended the *executable* `scripts/a1_fft_vulkan_cpu.cpp` to create correctly sized, readable/writable host-visible Vulkan linear images and descriptor views with the four original source-equivalent VkFormats, including explicit float16 round-to-nearest-even conversion, matching channel counts, robust row pitch bounds, true stored-channel sentinel tracking and fail-closed original format feature checks:

| Source-managed temporary format | Vulkan test view | Components | Bits/component |
|---|---|---:|---:|
| RGHalf | VK_FORMAT_R16G16_SFLOAT | 2 | 16 |
| RGFloat | VK_FORMAT_R32G32_SFLOAT | 2 | 32 |
| ARGBHalf | VK_FORMAT_R16G16B16A16_SFLOAT | 4 | 16 |
| ARGBFloat | VK_FORMAT_R32G32B32A32_SFLOAT | 4 | 32 |

The original `vkd3d` translated SPIR-V uses a *formatless* storage output image at descriptor set0/binding2, while `HLSL50 → glslang` emitted a typed `Rgba32f` output. The existing strict SHA-independent private `restore_formatless_write` diagnostic now runs **on the temporary roundtrip SPIR-V only**, reconciling its image declaration to the actual original and inserting `StorageImageWriteWithoutFormat`. Both original and reconstructed SPIR-V pass `spirv-val --target-env vulkan1.1` before dispatch. This never patches a Unity shader asset, silently downgrades a texture, changes a kernel index, or exports proprietary HLSL/DXBC/SPIR-V.

`scripts/probe_original_fft_software_vulkan.py` now compares each genuine original FFT compute variant against its independent roundtrip across all four real Vulkan image formats and three bounded seeds/dispatches (`0/1`, `19/1`, `257/2`). The output parser `tests/test_probe_original_fft_software_vulkan.py` strictly checks format, channels, precision, observed workload dimensions, actual written pixels and numerical deltas. No format result is inferred from an enum/count alone.

## Exact verified CPU-only evidence

- [**Source-only GitHub Actions 41734497370**](https://github.com/alwansan/raf/actions/runs/41734497370), **COMPLETED SUCCESS**, on `34e7f04d8571eed231758cb7ba70a04e39643833`; synthetic job **126260059133** and original job **126260229156** both SUCCESS.
- Existing unit tests per job: **10/10** source/output schema and format contract cases, **10/10** ZIP2 atomic reassembly corruption/no-overwrite controls. Synthetic canary and intentional `add → subtract` negative control still passed.
- The workflow fetched only the three ordinary-Git source parts of original `Raft_Data/sharedassets0.assets` from ZIP2 pin `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, reassembled and SHA-verified exactly **115,978,112 bytes**, original file SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; no Git LFS pull. The original ComputeShader `pathID=2456` raw-object SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247` was authenticated before extracting original 20 compiled DXBC variant slots. These slots are **not confirmed Unity runtime kernel indices**.
- Four original format layouts × 20 authenticated compiled variants × 3 distinct workloads = **240 authentic executable original-vs-roundtrip comparisons**, all genuinely dispatched through Mesa `VK_PHYSICAL_DEVICE_TYPE_CPU` Vulkan 1.1. Every pair produced real stored outputs; observed per-case written-pixel counts **64–2,048**. No skipped format or unclassified failure.
- **240/240** identical observed output components in the three selected workloads; **maxAbs = 0, maxRelativeL2 = 0, mismatched-written-coverage = 0**, nonfinite count = 0.
- Per format, `rg16f` **60/60**, `rg32f` **60/60**, `rgba16f` **60/60**, `rgba32f` **60/60**. The first three formats use the private formatless storage restoration; the last retains the prior typed RGBA32F baseline.

### Important red/green CI history

The first four-format attempt [CI41734092773](https://github.com/alwansan/raf/actions/runs/41734092773) **FAILED** intentionally fail-closed after 160 successful comparisons (first two scenarios ×20×4). Newly introduced optional `format` CLI argument increased argc to8; the old `if(argc==7)` condition skipped `dispatchGroupY` for the third scenario. The result validator rejected reported Y-group mismatch, correctly refusing to claim a complete run. A1 fixed to `if(argc>=7)` in exact commit `34e7f04d8571eed231758cb7ba70a04e39643833` and reran to SUCCESS240/240. This was a **test executor argument handling defect**, not proven original water shader failure.

## Precise acceptance boundary

This establishes **CPU software-Vulkan numerical and image write equivalence for these selected inputs and source-equivalent RG/RGBA float16/float32 image views only**. It narrows the original `Unknown`↔`Rgba32f` SPIR-V format identity concern for a controlled temporary reconstruction, but does **not** prove mathematical equality for every input, original two-pass full FFT topology, original Unity runtime kernel lookup, actual Unrealized Android ComputeShader import/ShaderLab pass binding, render pipeline textures/CB layouts, hardware Vulkan feature support on Adreno, visual fidelity, foam, waves, fire/color, installed APK, OBB, FMOD or runtime world state.

No raw decompiled game sources, shader bytecode, output images or original assets were committed. ZIP2, `main`, `zip`, `Unity-Editor`, CL, original `Raft` pointers, `.meta`/GUID, `.rgd`, LEFT Mouse0/500ms, Xbox/UGUI, scheduled tasks, native build requests and releases were not touched. W1 owns original ShaderLab graphics recovery, A12R the Blur constant-buffer investigation; neither scope was overwritten.

**WATER-001, RENDER-002 and FFT-FORMAT-009 remain OPEN for real integration; game NOT_READY with full immutable-candidate reviews 0/3.** A1's bounded CPU original-format compatibility scope is completed and paused. Next real cross-layer restoration: connect exact original FFT compiled variant and managed caller resource bindings to **authored Unity ShaderLab/ComputeShader** with validated real format/texture lifetime, then review supported physical Android GPU limits in coordination with independent rendering clients.
