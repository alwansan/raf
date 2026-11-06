# T1 scheduled — isolate real Unity FFT divergence after authentic paired Vulkan parity

- session_id: 20261106T1714Z-T1-scheduled-vulkan-unity-gap-q8n4
- origin: scheduled
- issue: WATER-001 OPEN; NOT_READY 0/3
- baseline_head: 4799d27b78631069e045354522009f675c6355f3 (2026-11-06T17:12:41Z)
- scope_commit: c01616b96d8aa85d0dbc06d4c594fff1988250f6
- work: prompt/coordination/work/WATER-001/20261106T1714Z-T1-scheduled-vulkan-unity-gap-q8n4.json
- source pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- origin=scheduled; no other session/state/MEMORY overwritten.

## Owner evidence before prioritization
Read docs/DEVICE_FEEDBACK_42058825739_AR.md. Owner entered, saved, exited, and reentered world using run 42058825739 artifact despite publication failure. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57: LogRaft 220911-559 had 23,884 water pass errors / 3,850 FFT kernel errors; 230108-327 had 39,132 / 6,026. These counts establish runtime symptoms, **not** which kernel or exact cause. This supersedes APK86 for device-world entry. T4 handles physical mouse; T5 handles three buttons/Resolution.

## New live evidence and discriminator
Read latest chat T1 session 20261106T170532Z-T1-chat-variant-declarations-7c4e and older 20261106T163310Z-T1-chat-real-fft-pair-d91e, scheduled 20261106T1608Z-T1-scheduled-pair-gate-regressions-k7p4, T1 state/MEMORY, and current Actions. Run 42254539826 is now **completed success** on fe3cff4899a19b197b64d692a28b2fdaf980fb7f; latest chat reports independent original-SPIR-V and translated-HLSL paired Vulkan traces with identical actual input/dispatch, 384 invocation reads [64,256,64], no fetch-coordinate/value mismatches and matched pass outputs for one 1024x32 seed19 one-group fixture. This is a genuine narrowing of the prior unpaired-data blocker. It **does not** establish Unity compiler/runtime parity.

Run 42258825614 is completed success at ec89ec09 for 11/11 source-only synthetic Unity variant/keyword checks. It does not compile or execute Unity C# probe. Prior Unity OpenGLCore negative run 42025620147 reports 63/64 and 31/32 pass mismatches and is not invalidated by same-Mesa-Vulkan parity. Therefore **first unclosed discriminating boundary** is actual Unity backend shader compilation/binding and readback, rather than another identical original-vs-HLSL Mesa Vulkan replay.

## Specific next executable experiment
1. Preserve exact original ZIP2 source hash and one 1024x32 seed19/1x1x1 dispatch input fingerprint. Stage verified candidate only in private scratch; no raw game binaries in public artifacts.
2. Record Unity 2021 OpenGLCore active graphics backend, ComputeShader asset GUID, kernel name, FindKernel result, GetKernelThreadGroupSizes, bound texture dimensions/formats, keyword enabled state, and Dispatch groups. Reject missing/unresolved mapping rather than treating 20 compiled program slots as 20 Unity kernels.
3. Capture bounded per-invocation keyed reads and output for the **same** fixture; compare first mismatching site/x/y/channel/ULP against already-authenticated original fixture. Distinguish shader compile/variant, input/binding, coordinate and arithmetic divergence. If Unity cannot produce authenticated keyed trace, report that boundary as BLOCKED, not a numeric mismatch.
4. Only then test a single targeted fix, followed by separate Adreno/phone verification. Avoid duplicate Unity/GPU runs while other T1 scopes own the same resource.

## What actually happened in this cycle
Read current owner evidence, live branch HEAD, latest T1 chat/scheduled handoffs and Actions, and registered independent work file c01616b. No source patch, new numerical GPU execution, CI dispatch, native build, or phone test occurred. This is an evidence-based experiment-selection checkpoint, not a completed engineering repair. Local git network access failed DNS resolution; GitHub connector reads/writes worked. No peer files, game assets, audio, Settings, touch, T4/T5 source or shared state modified. No Actions cancelled.

## Next resume
Re-read live HEAD and the T1 real-pair chat scope; coordinate resource ownership before Unity GPU run. Capture Unity OpenGLCore keyed evidence with same fixture and validate FindKernel/Dispatch. WATER-001 remains OPEN, NOT_READY 0/3.
