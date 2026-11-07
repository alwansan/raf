# T1 — Pinned phone LogRaft: kernel index 6 and Ultimate Water material breakdown

Date: 2026-11-07 UTC. Issue WATER-001 remains OPEN; NOT_READY 0/3.

## Evidence provenance

Owner's phone result is [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source e9c358eda01785b65e4eb14f18723da426635628; world enter/save/exit/reopen is owner-confirmed from Artifact, while Release publishing failed. Do not substitute APK86. The APK/OBB installed-file hashes are not verified here.

Read-only input: CL commit 520c4cf409aa20a4db54ff80ed87d8807d9cba57, `raft log/lf/LogRaft-20261105-{220911-559,230108-327}/session-summary.json`, fields `final_render_failure_breakdown` and `final_error_category_breakdown`. The former describes game-UID root Logcat messages, not distinct GPU invocations.

| Session | Spectrum invalid pass | Foam Global invalid pass | Other listed water materials | Total invalid pass | Invalid compute kernel index 6 | Other kernel indices |
|---|---:|---:|---:|---:|---:|---:|
| 220911-559 | 8,484 | 15,400 | 0 | 23,884 | 3,850 | 0 |
| 230108-327 | 15,028 | 24,104 | 0 | 39,132 | 6,026 | 0 |

Arithmetic checks: 8,484+15,400=23,884; 15,028+24,104=39,132. Foam Global accounts for ~64.48% and ~61.60% of the respective invalid-pass root counts. These are diagnostic category shares, **not** rendering-workload shares. All categorized invalid-kernel roots in these summaries refer to **index 6**. The first invalid pass and first index-6 root are 2ms apart in each session (timestamps from final category breakdown). Timing proximity is not causality.

## Narrowed hypotheses and discriminating test

1. `index 6` is an **observed rejected integer**; it does not establish a Unity `FindKernel` name, a compiled DXBC/SPIR-V program slot, or the same shader as Spectrum/Foam. Do **not** blindly add a seventh kernel or clamp to another index.
2. Spectrum and Foam Global are the only named invalid-pass materials in these two summary breakdowns. Check each material's serialized Shader GUID, active pass/keyword selection and runtime shader pass count separately from the FFT ComputeShader's serialized GUID and C# caller.
3. On an authentic Unity 2021 import with original source hashes verified, capture the FFT ComputeShader asset GUID, all `FindKernel(name)` requests/results, `HasKernel` checks, `GetKernelThreadGroupSizes`, `SetTexture`/`SetBuffer` bindings, and `Dispatch` groups at the first failure. The log must distinguish an invalid integer passed directly to `Dispatch` from a failed `FindKernel`, and identify the originating C# callsite. Record metadata only, never shader bytes or texture data.
4. Independently capture material GUID, shader GUID, pass index, shader.passCount, enabled keywords and renderer identity for the **first** Spectrum and Foam Global invalid-pass messages. A single common setup failure is a hypothesis until these per-material observations are obtained.
5. Only compare Vulkan and Unity numerical FFT traces after matching fixture/input hashes, dispatch dimensions, read site and invocation order; locate the first nonmatching pass, not the largest final error count. Existing comparator: `scripts/t1_fft_trace_first_divergence_7c3a.py`.

## Limits

No raw 33MB+ Logcat segment was ingested by this report; final summary categories cannot identify the full raw error text, caller, actual runtime `FindKernel` result, or shader asset identity. No Unity Editor/GPU/Android test or code fix is claimed. T4 owns physical mouse; T5 owns right-side buttons and Resolution. Preserve sound, Settings, saves, GUIDs and touch-layout deferral.

Session: `prompt/coordination/clients/T1/sessions/20261107T1308Z-T1-scheduled-kernel6-materialsplit-n4q7.md`.
