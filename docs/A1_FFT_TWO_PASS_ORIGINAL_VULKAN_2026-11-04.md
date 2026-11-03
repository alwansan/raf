# A1 — Original Raft FFT chained two-pass numerical execution

**Date:** 4 November 2026 (Asia/Baghdad). **Client:** raft-20261103T230900Z-a1f608bd. **Writable branch:** feature/android-native-port. **Code source:** [71906dbc3bd53166b05f0c9f97e64280a9c39482](https://github.com/alwansan/raf/commit/71906dbc3bd53166b05f0c9f97e64280a9c39482). **Original source:** read-only ZIP2 commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385.

## Source restoration and actual engineering

The earlier [240/240 single-stage FFT numeric experiment](https://github.com/alwansan/raf/actions/runs/41734497370) tested original compiled FFT programs individually in four authentic float16/float32 image views. It did NOT execute a genuine two-dispatch ping-pong graph.

This separate experiment adds three isolated testing tools:

- [Independent two-pass Vulkan C++ executable](../scripts/a1_fft_two_pass_vulkan.cpp): original first pass reads initialized source and butterfly images, writes an intermediate storage image; independent roundtrip first pass writes another intermediate. The command buffer issues explicit **Vulkan compute SHADER_WRITE to SHADER_READ image barriers** on both intermediate images. Each second pass then reads **its own first-pass output** plus the **same butterfly image** and writes its final result to independent output images. The host issues final write-to-host-read barriers, decodes real RG/RGBA half/float storage pixels and compares actual written channels.
- [SHA-authenticated private original program runner](../scripts/probe_original_fft_two_pass_software_vulkan.py): validates original serialized FFT ComputeShader, its 20 compiled positions, SHA-exact embedded DXBC payloads and compile-time workgroups. Checks each adjacent position pair's same original source/butterfly/target resource name digests. Independently translates original DXBC to VKD3D SPIR-V, HLSL50 via SPIRV-Cross and back to glslang SPIR-V; restores source-equivalent formatless storage image only in temporary private roundtrip binaries for half/two-channel format support.
- [Ten source-free controls](../tests/test_probe_original_fft_two_pass_software_vulkan.py) and [isolated CPU-only GitHub Actions workflow](../.github/workflows/raft-a1-fft-two-pass-vulkan.yml), which obtains only three pinned ZIP2 Git chunks for original sharedassets0.assets, with independent file SHA and object hash checks. No Git LFS, Unity/Android build, shader bytecode output, proprietary HLSL or pixel dumps.

Synthetic positive canary physically runs two original+roundtrip GLSL compute passes and checks known CPU result **input + 2 × butterfly**. An intentionally wrong *second* pass using subtraction produces a numerical mismatch. It therefore proves the harness detects a real two-pass arithmetic change rather than merely validating shader code.

## Exact completed GitHub Actions result

[**GitHub Actions 41737548860**](https://github.com/alwansan/raf/actions/runs/41737548860) **COMPLETED SUCCESS** on SHA 71906dbc3bd53166b05f0c9f97e64280a9c39482:

| Evidence | Verified result |
|---|---:|
| Synthetic canary job 126270519045 | SUCCESS |
| Original source + true two-pass job 126270676109 | SUCCESS |
| Synthetic schema/metadata controls | 10/10 |
| Two-pass known CPU-reference and wrong-second-shader negative | PASS / correctly rejected |
| Source owner sharedassets0.assets restored from read-only ZIP2 | 115,978,112 bytes |
| Source owner SHA256 | 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3 |
| Original ComputeShader pathID2456 raw SHA256 | 9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247 |
| Authenticated compiled FFT variants | 20/20 |
| Candidate adjacent compiled first/second pairs | 10 |
| Original format-equivalent Vulkan image views | RG16F, RG32F, RGBA16F, RGBA32F |
| Input/dispatch scenarios per format/pair | 3 |
| All actual two-pass image-output comparisons | **120/120 equal** |
| Per format | **30/30 equal** |
| Max absolute difference / relative L2 difference | **0 / 0** |
| Missing written pixel coverage / nonfinite outputs | **0 / 0** |
| Inconclusive shader pairs | **0** |

This is a material improvement over one-stage equality: **the original compute program pair is now executed with the intermediate produced by its own first stage, with genuine Vulkan memory synchronization and realistic packed half/float storage views**.

## Important boundary (no false completion)

Serialized adjacent compiled **program positions** are not yet proven identical to Unity's actual runtime **ComputeShader kernel indices** for every water quality/resolution choice. The source-managed caller two-pass offset+0/+1 and identical butterfly resource are separately supported by existing original C# audits, but the private two-pass test does NOT by itself install a Unity ComputeShader, recover all authored water passes, restore foam/material color or verify the shader compiles/executes on phone Adreno.

The tested three input/dispatch workloads are bounded and do not establish universal FFT mathematical equality, actual game frame render, the full row count/pipeline lifetime, original ShaderLab pass CB bindings, mesh/foam or device-support capability. Nothing in this experiment proves APK80 or a newer APK has these changes.

All original game assets, .meta/GUIDs, .rgd, input Mouse0, original data branches, zip2, CL, native build requests, current running workflows, Releases, and scheduled automations were left untouched. **WATER-001, FFT-FORMAT-009, RENDER-002 remain OPEN; project NOT_READY, immutable candidate absent, full independent readiness reviews 0/3.**

**Next real work:** source-authenticate exact Unity runtime kernel lookup and original ComputeShader asset identity, then integrate restored water/foam/ShaderLab resources in coordination with W1/W2/W3, using genuine graphics/device evidence before closing any blocker.
