# A1 authentic FFT SPIR-V arithmetic opcode profile — 3 November 2026

## Scope
Agent `raft-20261103T110728Z-b1c3478e`, branch `feature/android-native-port`, code SHA [`19884e775733feb49763b10b29ee19578dc4790d`](https://github.com/alwansan/raf/commit/19884e775733feb49763b10b29ee19578dc4790d). Extend *private CPU-only* DXBC-vkd3d-SPIRV-Cross-HLSL50-glslang inspection with a bounded SPIR-V opcode census: public arithmetic/conversions, selected control-flow opcodes, total extended-call counts. No shader names, program source, operands or binaries are written into public reports. The owner prohibits restoration-role Unity/APK/OBB/XAPK builds and forbids invented kernels/flags; this work did neither.

## CI verification

- [Synthetic run41625193607](https://github.com/alwansan/raf/actions/runs/41625193607), job125880661327 **SUCCESS** on exact code: six tests exercise known opcode counts, add-to-sub negative mutation, same histogram but changed operands (does *not* prove semantics), control/ext drift, malformed inputs and bad numeric counts.
- [Private original20 audit41625193741](https://github.com/alwansan/raf/actions/runs/41625193741), job125880662098 **SUCCESS** on exact code. Only three original LFS owners were hydrated behind SHA/size gates; original shader contents remain private. 20/20 authentic candidates translated and validated Vulkan1.1; 20/20 binding/workgroup signatures preserved.
- **New structural finding: 0/20 arithmetic/control/extension opcode profiles identical.** In all20 pairs the same three arithmetic opcode kinds differ, and `OpPhi` appears after roundtrip. Extended-instruction call **counts** are equal in each pair; this does not compare their imported instruction sets or operands.

| Public SPIR-V opcode | Original aggregate 20 | Recompiled aggregate 20 | Pairs differing |
| --- | ---: | ---: | ---: |
| OpBitcast (124) | 1050 | 1435 | 20/20 |
| OpIAdd (128) | 365 | 318 | 20/20 |
| OpIMul (132) | 205 | 140 | 20/20 |
| OpPhi (245) | 0 | 50 | 20/20 |

Other tracked arithmetic opcode counts matched within each pair; control-profile drift was OpPhi, and extension-call counts matched within each pair. Existing typed-image and image-operation/capability roundtrip profiles still preserve **0/20**. Arithmetic footprint difference can be explained by different compiler lowering and SSA representation; it does not establish changed output values, a game bug or proof that formatless shader patching is safe.

## Remaining gates

Authenticated Unity kernel index and complete ShaderLab/multipass paths, RenderTexture/view format binding, Adreno support, numerical execution of translated shaders and actual device/Unity water remain UNKNOWN/OPEN. Strict water authenticity gate stays false; WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN. APK80 source9462f8edd8cdb5becbccb96521f2876ef9924410 and old CL 2-Nov observations do not test this code. NOT_READY; no immutable complete candidate and reviews0/3. A1 did not change original resources/.meta/GUID/.rgd, LEFT Mouse0/500ms, existing native requests, releases, other agents, CL or tasks. A native run41624581951 on different source was already active from another agent and was not started/interrupted here.

A meaningful next experiment would compare operand graphs or execute authentic translated kernels against the CPU FFT oracle with explicitly matched formats, but avoid calling opcode-count equality numerical proof.
