# B06 — Original FFT Android capability instrumentation (4 November 2026)

## Scope and evidence

- Engineering source: [AndroidRuntimeLog.cs at 24f3607](https://github.com/alwansan/raf/commit/24f360712732c2dd4ef056751687ac3c1099e7fa). Isolated synthetic source-build lane: [workflow commit 9735146](https://github.com/alwansan/raf/commit/973514693569ac123bd87e75ebc1df50c3ae9bdc).
- Executed real C# `AndroidRuntimeLog.cs` with controlled synthetic Unity 2021 API stubs: [Actions 41913854292](https://github.com/alwansan/raf/actions/runs/41913854292), job `126868198656`, **COMPLETED SUCCESS**; observed marker `RAFT_B06_FFT_CAPABILITIES_SYNTHETIC success=true formats=4 failure_isolation=true logger_preserved=true unity_or_gpu_test=false`.
- Initial source HEAD observed `e8c312541b8139f2e889ff8921de8128146dcc84`; branch moves concurrently. Source code and tests affect only writable `feature/android-native-port`. No native request, Unity import, APK, release, game assets, original shader bytes, GUIDs, secrets or source branches changed.

## Concrete runtime improvement

The existing Android persistent startup logger already reported GPU/driver and generic `supportsComputeShaders`, but not the storage-write capabilities of the **four original GpuFFT RenderTexture requests**. It now emits a bounded once-per-initialization report:

- `water / fft_device_compute_limits`: Unity's `supportsComputeShaders` and `maxComputeWorkGroupSize` plus separate X/Y/Z reported limits; records `unity_compute_kernel_identity=unverified`.
- Four `water / fft_device_target_format` records, one each for `RGHalf`, `RGFloat`, `ARGBHalf`, `ARGBFloat`; for each, independently queries `SystemInfo.SupportsRenderTextureFormat` and `SystemInfo.SupportsRandomWriteOnRenderTextureFormat`. Failure of either returns `unavailable` **for that field**, not a fabricated boolean.
- Does not allocate textures, try to load original shaders, dispatch kernels, alter material passes, choose a fallback, change quality or affect UI. A failure of the overall capability probe emits an `unavailable` reason while leaving the base persistent logger operational.

This answers a *future device evidence gap* for four real source-requested formats while distinguishing texture view support from the missing authored compute kernel. A `True` capability result would **not** prove Unity's actual image format, physical device Vulkan feature flags, bound resource identity or pixel correctness.

Unity 2021.3 API references: [format random-write query](https://docs.unity.cn/2021.3/Documentation/ScriptReference/SystemInfo.SupportsRandomWriteOnRenderTextureFormat.html), [compute group invocation cap](https://docs.unity.cn/2021.3/Documentation/ScriptReference/SystemInfo-maxComputeWorkGroupSize.html), [2021.2 format support](https://docs.unity.cn/2021.2/Documentation/ScriptReference/SystemInfo.SupportsRenderTextureFormat.html).

## Synthetic negative controls and limitations

- All four enum requests logged exactly once, stable ordering; real `AndroidRuntimeLog.Initialize` idempotence tested.
- One synthetic `SupportsRenderTextureFormat` throws: only that format's support field becomes `unavailable`; all others survive.
- One synthetic `SupportsRandomWriteOnRenderTextureFormat` throws: only its field becomes `unavailable`.
- Synthetic `randomWrite=False` and `True` survive independently, avoiding optimistic default values.
- Synthetic `maxComputeWorkGroupSize` throws: an explicit optional-probe failure is logged, and core logger startup/future writes still function.
- Harness compiles the **actual modified Android C# source** against narrowly scoped public-API stubs, not Unity engine assembly/Android NDK. Successful managed compilation does not prove Android/Unity importer accepts source or runtime observations have been captured.

## Original game baseline and next action

Read-only [CL latest branch at 5394407](https://github.com/alwansan/CL/tree/5394407b5cd0a0ca1848ff0902f8d2133bf6ea29/raft%20log) retains installed APK86 logs. Latest session `20261104-225757-156` recorded final 40,327 invalid water shader-pass and 5,555 invalid compute kernel messages; index 6 with kernelCount 0 and Spectrum/Foam/Blur pass deficiencies. These are **old APK86 data**, not an outcome of this B06 source change.

When an independently justified signed game build is produced by coordinated native delivery, inspect the first startup `water/fft_device_*` lines together with actual original kernel/pass reconstruction and GPU program validation. If a format is reported unsupported, investigate actual requested mode and permitted fallback **without silent quality loss**. If all formats are supported, do not conclude WATER-001 fixed; the missing kernels/pass assets still dominate device evidence.

**Status: SOURCE_FIXED, synthetic managed CI confirmed; Unity/device UNVERIFIED. WATER-001 OPEN; NOT_READY, 0/3 complete immutable-candidate reviews.** Audio and Settings remain as owner-confirmed; touch/layout remain deferred.
