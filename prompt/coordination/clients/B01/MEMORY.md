# B01 — engineering memory

Session: `20261104T2105Z-B01-water-contract`. Track WATER-001 / FFT original managed callsite provenance (no shader rewrite). Earlier team guide, owner requirements and B review inspected. Active first-read HEAD: `6c966c63ba2eb303fc8a419ef7dd629230e81450`; successive concurrent B commits expected.

## Verified baseline and dependency
- B-team review: latest playable Raft APK86 [41812889049](https://github.com/alwansan/raf/actions/runs/41812889049), source d181ee7152580f49ee0b41dfd05fa2bfdacfafe5, not the later lograf releases.
- Historical [CL 2026-11-04 log](https://github.com/alwansan/CL/tree/5394407b5cd0a0ca1848ff0902f8d2133bf6ea29/raft%20log) shows water invalid passes, zero FFT kernels. Also independent SteamUserStats.StoreStats failure after WorldHasBeenLoaded. B50 works local Steam; B48 owns runtime FFT kernel identity; B49 shader pass guard. Avoid their files.
- No local workstation git network (container git ls-remote DNS error); GitHub connector permits read/write and Actions runs; cannot locally run all original-managed probe paths here.

## Engineering change and evidence
- Existing `scripts/probe_original_fft_kernel_callsites.py` scanned unfiltered original C# using regex, counting fake calls in comments/strings. SHA pin alone verifies the input text but cannot distinguish fake textual occurrences from real method calls.
- Implemented length/newline-preserving lexical masking of C# // comments, /* */ comments, ordinary/char/verbatim literals, before call regex and receiver capture. Original source remains used for balanced argument parsing, hashes and original line numbers. Raise on unterminated block comment/literal. This is source-only structural hardening, not a C# parser, not runtime provenance mapping.
- Added two regression tests: misleading commented/quoted callsites do not count, and unterminated comment fails closed. Code commits: [9b7096d](https://github.com/alwansan/raf/commit/9b7096d17bf557a8558737f63891b822936669cb), [3f493b1](https://github.com/alwansan/raf/commit/3f493b17adfd5b1f0f822c59bc980caf25d9df1d), escape corrections [d6146d8](https://github.com/alwansan/raf/commit/d6146d88ff0d3d3bb755faa502c8ff8ec6517a0a), [938dd13](https://github.com/alwansan/raf/commit/938dd139de855d41614f046cb8c2a6871501b2e5).
- [Initial CI 41911886307](https://github.com/alwansan/raf/actions/runs/41911886307) success at first code commit; later two intermediate runs cancelled (do not claim validated). [Final source 938dd13 CI 41911972796](https://github.com/alwansan/raf/actions/runs/41911972796) pending when checked. Run includes original managed ILSpy SHA-pinned source and independent numeric FFT tests; may change status after this checkpoint. No GPU/Unity/device proof.

## Checkpoint / outstanding
- Branch only feature/android-native-port; no force, no cancellation, no build request, no raw private game source publication. Audio/Settings untouched; touch deferred.
- Next check final CI 41911972796; if failures, inspect test failures and fix. Check whether mask should support verbatim C# escaped quotes in argument parser, interpolation and raw strings before broad trust. Compare sanitized original callsite counts to pre-change report; changes may be false-positive removals. For actual kernelCount=0, B48 runtime serialization correlation and shader restoration still open; WATER-001 remains OPEN, NOT_READY. Preserve exact .meta/GUID and original FFT programs.

## Verified final CI (2026-11-04)
[CI 41911972796](https://github.com/alwansan/raf/actions/runs/41911972796) completed success on final source 938dd13, job 126861846260. 64 synthetic tests; original SHA-pinned managed callers Dx11FFT Dispatch=2 SetTexture=6 (affine offsets 0/1), WavesRendererFFT SetTexture=10; FFT numeric oracle exit=0. The B01 scanner scope is complete, but WATER-001 and real Android GPU rendering remain unresolved. Next follow B48 kernel identity and B49 pass guards or pick different meaningful blocker.
