# Original butterfly FFT numeric reference experiment — 3 November 2026

## Scope and source provenance

This is a CPU-only numeric experiment. It does not change any game source, shader, original quality setting, asset, GUID, native build request or automation configuration.

Private inspection [41555160440](https://github.com/alwansan/raf/actions/runs/41555160440), sourcefa6d9d60a0b711a3954eb59f8a0b89df3f2feb1a, SUCCESS. The encrypted source packet was decrypted privately and all132 manifest hashes/source commit verified. No LFS was needed. The generator pins these exact original CSharp9 sources:

| Source | SHA256 |
|---|---|
| ButterflyFFTUtility | e1f7b56f6dca4a29d11b6db714809bdee4d9df2ca05fb6b9f27af47b66e459e1 |
| GpuFFT | 2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704 |
| CpuFFT | 31a455c417805bccc75c66874a070a6dd2cf72b67dfc95946c0eb2a076fb881f |

The private harness executes the complete original butterfly utility, the original GPU-table encoding method body and the original CPU FFT stage body. Generated source remains in temporary private runner files and is never uploaded. Logs expose only numeric summaries/error codes. The first harness compile had a Vector2 namespace collision; d57d00a94826508608bd21b8d34b793d0ff4ba7f replaces the broad numerics import with a Complex alias. This was a test harness compilation issue, not a new game/device failure.

## Independent comparison

For N=32,64,128,256,512 the harness generates original float/vector weight tables and checks their equality. It feeds impulse, constant complex, single-frequency and deterministic complex-random signals through:

- The actual original CPU FFT method, using complex offsets8/9 in the twelve-float record.
- A CPU replay of the original packed butterfly texture, for each of its two horizontal halves.
- The same replay with only table storage quantized to IEEE binary16, modeling the table format rather than all GPU arithmetic.

All are compared with an independent O(N squared), double-precision direct DFT using the negative exponent and no normalization. The reference convention follows the [NumPy FFT implementation definitions](https://numpy.org/doc/stable/reference/routines.fft.html#implementation-details); no fast FFT implementation is reused as the reference. Relative-L2 budgets are1e-5 for original CPU/full-float table and0.003 for binary16-table replay. Negative controls deliberately reverse stage order, conjugate weights or normalize incorrectly; each must disagree with the reference by more than0.1 relative L2.

The coordinate checks verify the encoded half-texel centers, reversed index row selection, second-half offsets and exact binary16 address representability for the tested sizes. Intermediate replay values use double-precision Complex; half intermediate render-target rounding is not modeled.

## Execution result

Original-source numeric CI [41555453779](https://github.com/alwansan/raf/actions/runs/41555453779), sourced57d00a94826508608bd21b8d34b793d0ff4ba7f: **COMPLETED SUCCESS**, job125653301781. Forty packed-table cases (full-float and binary16-table replay for both halves),20 original CPU FFT signal comparisons and194,887 checks passed. All three deliberately incorrect negative controls were detected. Maximum relative-L2 errors: full-float packed-table replay1.88937368177527e-7; binary16-table replay0.00023868836710026192; actual original CPU lane2.0495406296816126e-7. Execution exit0/errorCodes=[]. Local21 related Python tests passed, including fail-closed source fingerprints/ambiguity/output-location guards. Generation also passed locally against the three authenticated private source files. No local C# runtime execution is claimed.

## Acceptance limits and next work

Even successful numeric checks establish only the tested original CPU/table arithmetic and an authored point-sampling replay. They do not execute the original DXBC, translated SPIR-V/HLSL, Unity texture upload/sampling, mobile GPU, two-dimensional water pipeline or all CPU channel packing. The harness supplies integer stage counts for mathematical powers of two; it does not resolve original Mathf.Log rounding in the constructor. Actual per-water requested sizes and active phone quality remain unknown. Stored quality caps from the prior report do not establish runtime constructor size.

Do not infer Unity kernel-index enumeration from these results or equate this experiment with authentic shader recovery. Next compare translated original shader arithmetic/output against this numeric reference, including typed image formats, normalization, stage ordering and both passes. The strict water gate remains false. Full Unity/APK/OBB/XAPK/release hold remains active.

At review, the branch had no queued/in-progress native build; reviewed new cheap runs only. CL raft-log directory identities remained unchanged and APK80/source9462f8edd8cdb5becbccb96521f2876ef9924410 still has11 delivery assets. No new phone evidence was assumed.
