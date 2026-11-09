# T1 → T5 — Android FFT first-failure evidence in next authorized native build

Source [CI 42550454734](https://github.com/alwansan/raf/actions/runs/42550454734) **SUCCESS**: authentic pinned original managed Dx11FFT and GpuFFT CSharp9; two direct numeric Dispatch callsites preserved and Android-only trace hooks injected into exact original source after lifetime guard. Separate CSharp9 helper builds/runs with synthetic Unity API. This is NOT full Unity or phone acceptance.

## When next authorized full native game build runs
- Preserve .github/workflows/raft-unity-editor-android-import.yml T1 staging step immediately after `scripts.adapt_android_render_lifetimes`, with `--original-backup "$RUNNER_TEMP/original-render-lifetimes"` and `--managed-original "$RUNNER_TEMP/ilspy-src"`.
- Ensure only `android-port/Runtime/Platform/T1FftDirectDispatchTrace.cs` is copied with existing AndroidRuntimeLog helper; no `.meta` GUID, source Dispatch semantics or original shader asset modified.
- DO NOT start a Unity build just for this hook, edit native-request JSON, alter 5/5 XAPK trial vote or bypass authentic water gate. Keep Unity Editor compile proof pending until authorized build.
- On matching installed APK, inspect `raft-logs`/owner CL for `t1_original_fft_dispatch.before` and `t1_original_fft_dispatch.returned`, first 16 source calls, with `sequence`, `numeric_kernel_argument`, `original_exponent`, `inferred_bank_only`, `group_xyz`, `shader_instance_session_local`, `frame`. Use `logger.ready` metadata to pin same application session.
- Correlate first actual `water_fft_invalid_compute_kernel`/kernel index6 timestamp with the surrounding T1 before/returned event; absent T1 event is UNKNOWN (logger may be unavailable/budget exhausted), not proof Dx11FFT was uninvolved.
- `source_bank0_candidate` is a formula-derived candidate, not actual constructor bool; `.returned` means managed call returned, not GPU completed; no named `FindKernel` happens inside original Dx11FFT. Index6 still not mapped to original serialized compiled slot6/Unity kernel name. Do not report water fixed until actual device pixels and original shader resources independently verified.

T1 session: [20261109T0210Z-T1-chat-fft-dispatch-hooks-b6e4](../../clients/T1/sessions/20261109T0210Z-T1-chat-fft-dispatch-hooks-b6e4.md). WATER-001 remains OPEN, full game NOT_READY0/3. No APK generated here.
