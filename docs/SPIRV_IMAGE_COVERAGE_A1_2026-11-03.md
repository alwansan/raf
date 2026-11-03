# A1 synthetic SPIR-V image use coverage — 3 November 2026

**Scoped result:** diagnostic source/test correction, NOT shader restoration. Client `raft-20261103T104800Z-a1f742c0`, commit [13bd0330904b48eb58fad73e27b7299e0d08b230](https://github.com/alwansan/raf/commit/13bd0330904b48eb58fad73e27b7299e0d08b230).

## Reproduction

A synthetic validly encoded wordstream with a direct write/read and an additional `OpImageSampleImplicitLod` referencing untracked ID199 yielded `all_image_operations_uniquely_traced=true` before repair. Ignored instructions did not appear in any operation category. This is a scanner integrity negative control, not a claim that an original game shader has that defect.

## Change and evidence

- Include core image sample87-94, gather96-97, query101-107, sparse image305-315 and320, texel pointer60. Reject truncated recognized instructions; keep original write/fetch/read categories.
- Correct pointer alias list: OpInBoundsPtrAccessChain70 added; OpArrayLength68 removed (it computes integer length and must not fabricate a pointer image alias).
- Synthetic local:17/17 Python unittest PASS, after extra negative case failed before change. Exact code SHA [13bd0330904b48eb58fad73e27b7299e0d08b230](https://github.com/alwansan/raf/commit/13bd0330904b48eb58fad73e27b7299e0d08b230) independently passes [GitHub Actions41622977666](https://github.com/alwansan/raf/actions/runs/41622977666), job125873109925,17 fixture tests reported in full job logs.
- [Private authenticated original resource audit41622977691](https://github.com/alwansan/raf/actions/runs/41622977691): completed/success at documentation checkpoint; authenticate actual CI before using its results. [Khronos SPIR-V spec](https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html) gives documented operand positions.

## Boundaries

Fixture wordstreams are not complete typed shaders validated with spirv-val. Vendor/image extensions not exhaustively included. Image operand tracing does not establish compiler arithmetic/format, Unity kernel indices, two-pass FFT, GPU execution, game world, or Android rendering. This work has no effect on APK80 or physical device; WATER-001/RENDER-002/FFT-FORMAT-009 OPEN, NOT_READY and no candidate/three reviews (0/3). No originals, .meta/GUID, touch, native requests, task or release changed.
