# B06 — Source-grounded FFT workgroup limits on Android (2026-11-04)

## Engineering scope

The existing B06 Android startup logger introduced in [24f3607](https://github.com/alwansan/raf/commit/24f360712732c2dd4ef056751687ac3c1099e7fa) measured Unity GPU support for RGHalf/RGFloat/ARGBHalf/ARGBFloat but emitted ambiguous names `max_group_x/y/z`. In Unity **2021.3**, `SystemInfo.maxComputeWorkGroupSize` is the largest **total local workgroup invocation count**, whereas `maxComputeWorkGroupSizeX/Y/Z` bound **dispatch group counts**, not the local `[numthreads(x,y,z)]` values. Confusing them could incorrectly label a 1024-local-invocation authentic compute candidate as accepted by a high dispatch-count limit.

Official Unity 2021.3 API references:
- [Total local workgroup invocation limit](https://docs.unity.cn/2021.3/Documentation/ScriptReference/SystemInfo-maxComputeWorkGroupSize.html)
- [X dispatch group count limit](https://docs.unity.cn/2021.3/Documentation/ScriptReference/SystemInfo-maxComputeWorkGroupSizeX.html)
- [Random-access-write texture format support](https://docs.unity.cn/2021.3/Documentation/ScriptReference/SystemInfo.SupportsRandomWriteOnRenderTextureFormat.html)

## Actual integrated change

[Source commit f9e34ee](https://github.com/alwansan/raf/commit/f9e34ee647e8eb841fa3a960f01cef5eb2a6be87) updates `android-port/Runtime/Platform/AndroidRuntimeLog.cs`. The native project export workflow already copies this file into temporary Unity Assets/Platform; that workflow was not edited.

- `water/fft_device_compute_limits` emits `max_group_invocations` separately from **`max_dispatch_groups_x/y/z`**, a `reported_max_is_theoretical=true` caveat, and `original_runtime_kernel_mapping=unverified`.
- `water/fft_original_compiled_group_limit` emits five *source-authenticated compiled-candidate* local group sizes, 64/128/256/512/1024 (Y=Z=1). Each includes source FFT resolution 32/64/128/256/512 and only a theoretical comparison with the per-group invocation limit.
- Each capability lookup independently handles exceptions and zero/negative driver values as `unavailable`. A failed dispatch-axis read or local-group limit read **does not discard** the four format / random-write capability records. There is no inference of a working ComputeShader.
- The new code allocates no RenderTexture, reads no original shader bytes, emits no fake `FindKernel` indices, dispatches no compute jobs and does not alter quality, water/math, passes, graphics API, sound, Settings, UI, .meta/GUID or .rgd.

The five original local group sizes are backed by the independently authenticated original GpuFFT/DXBC source and same-slot Unity serialized metadata, e.g. [B48 original selector/source authenticated CI 41912422220](https://github.com/alwansan/raf/actions/runs/41912422220) and [B18 compiled SHEX/Unity parity CI 41922333604](https://github.com/alwansan/raf/actions/runs/41922333604); this is *not* evidence that each original compiled slot is a runtime Unity Kernel ID. B08 independently found one shared serialized kernel name across all 20 compiled entries. Only compile/runtime provenance would settle the actual identity.

## Verifiable execution

[Test revision 2fa36d1](https://github.com/alwansan/raf/commit/2fa36d110cbaf1693cd61fbede26e7ce3e8f8d36) compiles the **actual modified Android logger source** with synthetic Unity 2021 API stubs using `dotnet run --project tests/b06_fft_caps_smoke/B06FftCaps.csproj --configuration Release --nologo`. New negative and boundary cases:

1. Theoretical maximum 1024 includes all five candidate group sizes, including exact equality at 1024.
2. Theoretical maximum 512 includes 512 but flags source group1024 as exceeding; no fallback or change of runtime resolution occurs.
3. Failed dispatch-Y API query is logged `unavailable` without suppressing four format and five group records.
4. Failed and nonpositive per-workgroup limits are not treated as zero or proof of incompatibility; every assessment remains `unavailable`.
5. Unity runtime kernel identity and actual FFT dispatch remain explicitly unverified; logger still reports normally and is idempotent.

[**CI 41928357485**](https://github.com/alwansan/raf/actions/runs/41928357485), source `2fa36d110cbaf1693cd61fbede26e7ce3e8f8d36`, job `126918624071`: **COMPLETED SUCCESS**. Exact recorded marker: `RAFT_B06_FFT_CAPABILITIES_SYNTHETIC success=true formats=4 compiled_groups=5 limit_1024_inclusive=true limit_512_rejects_1024=true unknown_limit_safe=true exception_isolation=true logger_preserved=true unity_or_gpu_test=false`.

**Red/green incident:** [41928250212](https://github.com/alwansan/raf/actions/runs/41928250212) failed after source-only update because the old synthetic test asserted one exceptional property would abort the entire optional probe and emit `fft_device_capabilities.unavailable`. The new code intentionally isolates the failed capability and preserves all other facts. Updated test assertions plus new boundaries passed in 41928357485. This is a stale test expectation, **not** an original shader/compiler/device fault.

## Evidence improvements for previous B06 scope

The earlier [B06 original FFT Dispatch lexical guard](B06_FFT_DISPATCH_LEXICAL_GUARD_2026-11-04.md) previously cited only [eight synthetic checks 41914612977](https://github.com/alwansan/raf/actions/runs/41914612977). In this resumption we also inspected the workflow run automatically triggered by the original source/test edits: [**41914575997**](https://github.com/alwansan/raf/actions/runs/41914575997), job `126871078150`, **SUCCESS** against original SHA-checked source. Its authenticated stage executed `scripts.probe_original_fft_resource_bindings` after hydrating the pinned original file and privately decompiling CSharp9; observed original `compiled_slots_with_csharp_resource_names_matched=20`, both Dispatch shapes and intermediate resource flow checked. This strengthens the scanner source-validation evidence, but not actual Unity/Android FFT execution. Intermediate malformed source commit `78e926f` had CI [41914491728](https://github.com/alwansan/raf/actions/runs/41914491728) FAIL due an indentation syntax error and was corrected before the authenticated green runs.

## Remaining boundary

Source-supported *theoretical* limit inference cannot establish actual Vulkan `shaderStorageImageWriteWithoutFormat` feature, chosen Unity graphics image view, driver/compiler variant, kernel/resource identity, pass order, foam/water pixels, game performance, or playable world. No Unity Editor import or device test ran here. Latest Raft device test remains APK86 / [41812889049](https://github.com/alwansan/raf/actions/runs/41812889049) with original water and local-world failures. These source modifications are absent from that installed binary. When a coordinated newer APK becomes available, inspect its saved `water/fft_device_*` and `water/fft_original_compiled_group_limit` startup rows, correlate with actual kernel assignment and real Adreno device execution. Do not label supported theoretical limit as recovered water.

**B06 scoped work SOURCE_FIXED / synthetic CI SUCCESS; previous original source parser additionally AUTHENTICATED INPUT CI SUCCESS. WATER-001 OPEN, NOT_READY 0/3 independent full reviews.**
