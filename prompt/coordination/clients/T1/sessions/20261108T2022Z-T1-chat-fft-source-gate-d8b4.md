# T1 chat session — 20261108T2022Z-T1-chat-fft-source-gate-d8b4

**identity:** T1 | **origin:** chat | **issue:** WATER-001 (OPEN)  
**resumed_from:** `20261108T1924Z-T1-chat-raw-root-context-a7d9` and latest `20261108T1910Z-T1-scheduled-axis-identity-f4c8`  
**base_sha:** `fa3d282481c5ac499decf5dd30b89cb6d1acbbb1`  
**scope:** repair a proven T1 FFT source regression; audit the exact original managed Raft CSharp FFT first/second Dispatch numeric selector for the LogRaft index-6 hypothesis. **No original shader/Unity/device/APK change.**  
**work:** `prompt/coordination/work/WATER-001/T1-20261108T2022Z-T1-chat-fft-source-gate-d8b4.json`  
**experiment_key:** `fft-original-index-source-binding-v1-original-Dx11FFT-sourceSHA-and-Unity-serialized-FFT-objectSHA`  
**resource_key:** original SHA-pinned `Assembly-CSharp.dll` + original ILSpy `Dx11FFT` and `GpuFFT`; source-only Actions runner (not T5 native Unity mutex).

## Restored team context

Live branch had no active T1 GPU run at scope claim, but T5/T3/T2 workflows were ongoing, none cancelled. Original owner-reported game is separate from Team Mini. One unified Android Mini r3 was already built and r4 Surface screenshot fix was being delivered; T1 has **no** new GLES driver changes. T2 reports **real Android Adreno 730 GLES T2-01..04 PASS** from owner CL/test, *not proof of original Raft water*. The first real owner CL raw T1 source [CI42516813516](https://github.com/alwansan/raf/actions/runs/42516813516) passed, but showed no directly captured invalid kernel root in that first segment; the full-session collector separately reports index6 errors and `Dx11FFT` lexical evidence cannot map them to a named Unity kernel.

## Engineering 1 — repair real T1 paired FFT diagnostic regression

- [CI42518408573](https://github.com/alwansan/raf/actions/runs/42518408573) **FAILED** before tests at `scripts/t1_fft_first_divergence.py` line81. Git source contained an actual literal `\n` escaped text between function arguments, producing Python `SyntaxError: unexpected character after line continuation character`; this is a real code regression, not a Unity FFT computation mismatch.
- Fixed Python `json.loads` to a syntactically correct multiline invocation, [commit 90b0ebe9](https://github.com/alwansan/raf/commit/90b0ebe915f1d6594089dfc7ca683c24f878132b), without changing FFT tolerances, readback, game source or original data.
- [CI42519336164](https://github.com/alwansan/raf/actions/runs/42519336164) **COMPLETED SUCCESS**: full T1 existing paired diagnostic regression suite now imports and runs. Neither run executes Unity/Adreno.

## Engineering 2 — authenticated original FFT kernel6 *numeric source argument*

- Added `scripts/t1_fft_original_kernel6_candidates.py` [fd14fe5](https://github.com/alwansan/raf/commit/fd14fe5b8e3d5328833e0fdb44d6e0dd96ff619d), `tests/test_t1_fft_original_kernel6_candidates.py` [a183ee8](https://github.com/alwansan/raf/commit/a183ee8c253eccb7cde940d0042533806d35ee67), source-only CI `.github/workflows/raft-t1-fft-original-kernel6-candidates.yml` [fed9e62](https://github.com/alwansan/raf/commit/fed9e62b623323c82efd4c708514ebc417a9c04e). The tool *reuses* SHA-aware original `probe_original_fft_inherited_seed` and `probe_original_fft_kernel_callsites` and inverts exact source selector ONLY as conditional integer cases; it never uses compiled slot numbers as runtime `FindKernel` IDs.
- Authentic tracked original PC DLL `Raft/Raft_Data/Managed/Assembly-CSharp.dll`: 3,211,776 bytes, Git blob `fc9d4ba920a178fdb89c970d9d772a01051dadc6`; private pinned `ilspycmd v11.2.0.10050` CSharp9 produced class SHA `Dx11FFT=8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0`, `GpuFFT=2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704`. No private C# exported, no shader binary, no artifact.
- **Proven original source arithmetic:** inherited `n=integer truncation of Mathf.Log(size)/Mathf.Log(2f)`; first and second pass numeric Dispatch indices have `((n-5)<<1)+(bankFlag?10:0)+passOffset`, pass offsets `0,1`. For the purely conditional integer n=5..9/bank0,1/pass0,1 sample domain, **numeric argument 6 occurs only for size256 (n8), bank0, pass0**; second pass argument 7. Hypothetical size256 bank1 yields 16,17.
- Real source is SHA authenticated: **2 `Dispatch`, 6 `SetTexture`, same receiver**, offsets `0,1`, and **0 `FindKernel` calls within `Dx11FFT`**. This is not proof that another module does not use FindKernel or that an Android runtime had an original registered kernel6.
- [CI42519731107](https://github.com/alwansan/raf/actions/runs/42519731107) initial **SUCCESS** (15 new +5 inherited +9 callsite =29 synthetic and genuine original source audit). Added anti-false-proof case to show even synthetic FindKernel mention cannot prove Unity ID [667fd56c](https://github.com/alwansan/raf/commit/667fd56cdaebc3ed2d3dae81865ca3a168ae1e3f) and strict *actual zero* FindKernel assertion [f51c4e26](https://github.com/alwansan/raf/commit/f51c4e26d340a5db3f9b8781506e3e53dc180e2e).
- **FINAL CI:** [42519853981](https://github.com/alwansan/raf/actions/runs/42519853981) **COMPLETED SUCCESS** at `f51c4e26d340a5db3f9b8781506e3e53dc180e2e`: 16 T1 cases + 5 inherited seed + 9 original caller (**30/30 tests**) and actual SHA-pinned original DLL, ILSpy class SHA verification, conditional argument6 case and source-class FindKernel0. `NO_ORIGINAL_MANAGED_SOURCE_EXPORTED=true`, `NO_ANDROID_APK_OR_UNITY_EXECUTED=true`.

## Limits, handoff and next falsifiable task

**Never write** that the Logcat rejected runtime `kernel index6` is the original `Dx11FFT` named kernel, matches compiled `slot6`, occurred at size256/bank0, or that water was repaired. No phone FFT state, compute asset GUID/instance, runtime shader import, name-to-kernel mapping, keywords, binding, GPU dispatch or numeric pixel comparison has been observed. The first raw segment lacked literal kernel message even while the *separate* collector proves kernel6 count. A source numeric selector consistent with6 is only a narrowed hypothesis.

[Final original source report](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T1_FFT_ORIGINAL_KERNEL6_SOURCE_CASE_2026-11-08.md) with exact provenance/limits and on-device next capture plan. T5 should instrument first failure in next approved **full game** build to log actual FFT resolution, fourth constructor bank boolean, computed numeric indices, original shader asset GUID hash/name lookup behavior, per-pass target texture dimensions and Dispatch groups at failure. **Do not run private Unity 2021 Editor again without fixing source-free license preflight**; previous private container proved an activation problem. Only after real same-build resource identity should serialized program mapping and first numerical divergence be attempted.

The first shared APK and subsequent Arabic portrait/SurfaceView Mini remain T5-owned. T1 only changes source-only Python/CI/reports. **T1 shared Mini round r4 NO_BUILD**; independent full game trial vote remains **NO_BUILD** from FFT until original functional fix. **WATER-001 OPEN, full readiness NOT_READY 0/3**. No work in T2/T3/T4/T5 files, native build request, protected branches, or private game distribution.

**status:** COMPLETED. **next_step:** coordinate same-build original FFT runtime first-failure metadata with T5 (and Spectrum/Foam with T2), then compare original source/serialised binding and Adreno water pixel evidence; no repeat same source-only test without new evidence.
