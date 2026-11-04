# B48 — authenticated original FFT source selector × compiled program compatibility

- Session: `20261104T2058Z-B48-f24a`
- Issue: WATER-001 (P0); track water-fft, independent of B47/B49 ShaderLab pass and B50 Steam-local work.
- Branch: `feature/android-native-port`
- **Verified green run:** [41912422220](https://github.com/alwansan/raf/actions/runs/41912422220), code/test source `7be4c3365d4297a06abf502ceea504fee507f9c4`. Original initial run [41912253262](https://github.com/alwansan/raf/actions/runs/41912253262) failed due to B48 test fixture assertions; incident below. No production bypass introduced.
- Changes: `scripts/probe_b48_fft_selector_program_compat.py`, `tests/test_probe_b48_fft_selector_program_compat.py`, `.github/workflows/raft-b48-fft-kernel-identity.yml`. No .meta/GUID, original assets, game runtime, native build request or protected branches modified.

## Authenticated inputs / controls

Private original ZIP2 provider commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, only three split parts of `Raft_Data/sharedassets0.assets`, restored in ephemeral runner staging, original **115,978,112 bytes**, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, no LFS. Original `ComputeShader` pathID `2456` SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`; exactly 20 compiled DXBC slots independently correlated by SHA/bytes against the serialized variant table.

Private ILSpy CSharp9 of existing managed original DLL, `Dx11FFT` normalized source SHA256 `8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0`; inherited `GpuFFT` source SHA256 `2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704`. Existing source proofs establish `n = truncate(log(r) / log(2))` and candidate selector `((n-5)<<1) + (fourth_bool ? 10 : 0)` for first pass, next pass +1. B48 newly fail-closed joins *both independently verified authentic evidence chains*: for each of 5 source sizes and 2 source banks, the two selected serialized compiled candidate positions have exactly `[2*r,1,1]` source-authenticated threadgroup shape. Every one of 20 compiled positions is covered exactly once; no aliases/changed indices accepted.

| Source FFT r | n | Bank 0 compiled candidate slots | Bank 1 compiled candidate slots | Verified serialized threadgroup x |
|---:|---:|---:|---:|---:|
| 32 | 5 | 0, 1 | 10, 11 | 64 |
| 64 | 6 | 2, 3 | 12, 13 | 128 |
| 128 | 7 | 4, 5 | 14, 15 | 256 |
| 256 | 8 | 6, 7 | 16, 17 | 512 |
| 512 | 9 | 8, 9 | 18, 19 | 1024 |

B48 synthetic contract 5/5 + previous inherited selector 5/5 + original serialized variant tests 5/5 all pass; deliberately mutated source selectors, source bank, swapped slots, bad SHA-structure witness, mismatched workgroups, falsely asserted runtime proof are all rejected. Private real-data CI also passed after SHA-pinned ZIP2 reconstruction and original CSharp9 recovery. No shader bytecode/private game source or pixels exported, and no image/device frame test occurred.

## Proven and unproven, explicitly separate

**SOURCE/CANDIDATE-CORRELATED:** Original C# selector values are consistent with exactly 20 authentic serialized compiled FFT programs and their group sizes for 10 source-selected *candidate* two-pass operations. This is a cross-evidence compatibility gate beyond A1's independent candidate-pair numerical comparison; it does not manufacture shader kernels or change runtime.

**NOT PROVEN:** whether Unity original runtime kernel indices used by `Dispatch` map in that order to the 20 serialized compiled variants. Those entries share a kernel-name identity; count/position is not a proof of 20 Unity-addressable kernel IDs. No Unity Editor compilation of restored authored .compute source, Adreno workgroup capability check or actual native water/foam rendering was done. In particular original shader workgroup x=1024 is a GPU compatibility question until actual target capability and runtime dispatch are verified; it must not be assumed supported or rejected from this source alone.

**Remaining P0:** exact Unity kernel ID/source binding and authentic .compute reconstruction; Water Spectrum/Foam/Blur authored pass restoration; platform resource/image lifetime; Unity and phone validation that resolves APK86 `kernelCount0` and missing passes. WATER-001 remains OPEN, project **NOT_READY / 0 of 3 full reviews**.

## Initial failed fixture / correction

Run [41912253262](https://github.com/alwansan/raf/actions/runs/41912253262) failed on B48's own synthetic fixture: the result deliberately lists source-size rows with alternating banks, but two expected positions were read as if bank0 rows were contiguous; a deliberately wrong bank selector was accidentally unchanged; one negative workgroup mutation equaled its original value. No authenticated original input or production adapter was reached in that red job. Commit [7be4c336](https://github.com/alwansan/raf/commit/7be4c3365d4297a06abf502ceea504fee507f9c4) corrected only expectations/mutations; re-run [41912422220](https://github.com/alwansan/raf/actions/runs/41912422220) passed all 15 tests and original-data stage. Reject the hypothesis that the first red job proved shader/index mismatch.

## Resume point / next independent engineering hurdle

Recover **typed Unity runtime compute kernel ID mapping** or instrument an isolated Unity 2021.3.45f2 private test with authentic staged ComputeShader to observe actual `FindKernel` identities and real index-to-program selection; do not infer it from this candidate matrix and do not set `authentic_water_kernel_identity_verified`. Coordinate with B47/B49 so their water pass ShaderLab work is not duplicated. Preserve owner-observed functional audio and Settings; input/touch/layout development deferred.
