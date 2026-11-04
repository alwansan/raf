# B06 — FFT original resource binding Dispatch lexical hardening, 4 November 2026

Session `20261104T210726Z-B06-fmt6a2` / branch `feature/android-native-port`. This is source-audit correctness engineering, not shader/kernel recovery or device proof.

## Defect and repair

The original FFT resource-binding correlator first calls the established SHA-pinned `analyze_source` to verify actual compute API call sites while filtering comments and strings. However a second dispatch-shape verifier used `CALL.finditer(source)` on **raw** original C# text. A commented-out `Dispatch` or quoted illustrative call could appear as an extra real dispatch in this secondary audit, making the authentic source fail for a non-executable token. That is a false-positive source-integrity failure, not a runtime cause of the APK86 water failure.

[Source fix df784a6](https://github.com/alwansan/raf/commit/df784a6ab821f3dbbfbe7ea47293e16f3edba11e) changes the secondary scanner to `CALL.finditer(mask_noncode(source))`, sharing the already existing B01 lexical masker. The masker preserves character positions while replacing comments/quoted literals with whitespace; `parse_original_args(source, ...)` therefore still extracts the exact original actual call arguments at their proper offsets. The first accidental commit `78e926f3` used literal backslash-n in a new source comment and was immediately corrected by `df784a6` before the test workflow. Do not reuse the intermediate commit as a candidate.

[Adversarial tests f322497](https://github.com/alwansan/raf/commit/f32249794d8ccf4f5711ae16bab093e209c830e2) insert synthetic fake `Dispatch` in single-line comment, block comment, ordinary quoted string and verbatim string, then require the two real dispatch calls to remain source-authenticated. A negative control removes the real second dispatch while leaving fake text; the auditor must reject it. Original existing negative controls for row count, dispatch offset, resource aliases, SHA and compiled workgroup identity remain intact.

## Executed CI

Isolated [B06 FFT resource lexical workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-b06-fft-resource-lexical.yml) commit `f4b9520c367bf8e78fcfebba673f20b465edb720`, [run 41914612977](https://github.com/alwansan/raf/actions/runs/41914612977) at exact source SHA `f4b9520c367bf8e78fcfebba673f20b465edb720`, job `126870861595`: **COMPLETED SUCCESS, 8 of 8 synthetic unit tests PASS**. No original private data or raw bytecode was required or exported, no LFS, Unity import, GPU, APK, OBB, native request or release.

**Limits:** tests are synthetic resource metadata and C# text; this source revision was not revalidated against live decompiled original DLL/private ComputeShader in this run. Older authenticated private source CI is contextual evidence, not equivalent to rerunning the modified scanner on original source. This fix prevents **false source-audit Dispatch records**, not missing original FFT or water shader runtime kernels.

**Disposition:** B06 resource lexical guard SOURCE_FIXED + CI synthetic-tested, original-data recheck and Unity/device remain UNVERIFIED; WATER-001 OPEN; project NOT_READY / 0 of 3 full reviews.
