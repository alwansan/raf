# T1 — private Unity FFT producer stage and original-derived candidate SHA guard

- **session_id:** `20261106T2017Z-T1-chat-private-producer-gate-8f31`
- **origin:** `chat`
- **base_sha:** `afb519b625b6c346420153caa88b4c40972d44de`
- **resumed_from_sessions:** `20261106T195959Z-T1-chat-ci-log-pin-7b42`, `20261106T2015Z-T1-scheduled-native-fft-gate-x4q9`, `20261106T1942Z-T1-chat-auth-producer-bridge-62a9`.
- **issue:** WATER-001 OPEN / NOT_READY 0/3. T1 trial vote `trial-20261106-r1`: **لا يحتاج**, unchanged.
- **scope:** `prompt/coordination/work/WATER-001/20261106T2017Z-T1-chat-private-producer-gate-8f31.json` (completed).
- **experiment:** `prompt/coordination/experiments/T1/20261106T2017Z-T1-chat-private-producer-gate-8f31.json`.
- **event:** `prompt/coordination/B_TEAM/events/T1/20261106T2017Z-T1-chat-private-producer-gate-8f31.json`.
- **T4/T5 evidence handoff:** `prompt/coordination/B_TEAM/events/T1/20261106T2017Z-T1-chat-private-producer-gate-8f31-native-compile-handoff.json`.

## Evidence restored and boundaries

Reread T_TEAM RESTORE_AR, CHAT_AND_SCHEDULE_AR, trial vote, most recent chat `195959Z` and scheduled `2015Z`, current HEAD and branch Actions. Scheduled T1 work `20261106T2015Z-T1-scheduled-native-fft-gate-x4q9` is evidence-only and did not edit the four scoped files. Our chat reserved its own WATER-001 work before editing commit [55aa696](https://github.com/alwansan/raf/commit/55aa6969599b02c97a6f0d53fa2bb27354f4eb65). No full Unity dispatch and no T2–T5 source touched.

Previous proof [42285401655](https://github.com/alwansan/raf/actions/runs/42285401655): three historical CI markers physically matched original Input signed-bitcast vs translated Phi vs Unity computed-carrier zero63 sourcefree evidence, but it was **not** same-context original-vs-Unity numeric result. Prior paired source gate [42285338050](https://github.com/alwansan/raf/actions/runs/42285338050) source-only controls, not actual paired game capture. Owner's phone artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) entered/saved/reopened world, still water/colour defects.

## Concrete change

1. [New private Python gate](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/t1_fft_unity_trace_producer_gate.py): only after existing direct original SPIR-V and Unity input/trace validation, insist on Unity C# `T1ReplayStage.txt == complete`, original-derived ZIP2 ComputeShader object SHA, 2 specific compiled slot rows 0/1, generated resource property roles, expected 64 group size, and **actual physical SHA256 of both FFT_Candidate_00/01.compute**. Cross-bind injected `T1TracePass0.compute` and Unity `trace.bin` to private pair manifest SHA, require OpenGLCore GPU CopyInput marker. Symlink, alias, extra fields, duplicate JSON, bad types, stale stages and malformed sizes reject. Output only safe counts/flags; neither original bytes nor private identifiers leak. **C# stage marker remains UNSIGNED**: no independent compiled shader attestation claimed.
2. [New 15 adversarial controls](https://github.com/alwansan/raf/blob/feature/android-native-port/tests/test_t1_fft_unity_trace_producer_gate.py). [T1 source-only workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-t1-fft-private-unity-paired-bridge-ci.yml) extended by [b0b934d](https://github.com/alwansan/raf/commit/b0b934d601714ebd6c7669a5a955fed41b2910bc).
3. [Original T1 Unity private opt-in workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-t1-fft-unity-input-identity.yml) invokes extra stage gate **AFTER** existing direct-original/Unity paired capture, **BEFORE** numerical comparison. Change [3f618bb](https://github.com/alwansan/raf/commit/3f618bbbd12d94f3424811ac1019a725867ec48d). Retained owner opt-in requirement, mutex `raft-native-engine`, `cancel-in-progress:false`, ZIP2 immutable pin, no private file upload.

## Actually tested

- [**GitHub Actions 42287568433**](https://github.com/alwansan/raf/actions/runs/42287568433) @ `b0b934d601714ebd6c7669a5a955fed41b2910bc`, job `128132253694`: **COMPLETED SUCCESS**; decoded logs: **21/21 existing direct pair**, **17/17 existing input join** and **15/15 new producer-stage SHA test** passed, total **53/53** synthetic/source-only checks.
- Regular push of opt-in private Unity workflow did **not** start the GPU job: [42287573222](https://github.com/alwansan/raf/actions/runs/42287573222) **SKIPPED**. Separate paired diagnostic workflow [42287573238](https://github.com/alwansan/raf/actions/runs/42287573238) SUCCESS. No native/Unity license build generated; this protects other workers.

### Native build failure found and handed off

Owner-direct [42281310905](https://github.com/alwansan/raf/actions/runs/42281310905) at source `d692400115c36c4839fa4f4954e5f6ed1c60d413` **COMPLETED FAILURE** in reconstruct job `128111384362`, Unity 2021 Android script compile. Logs contain **10 distinct CS0234 references** (displayed twice) to missing `RaftAndroid.Platform.AndroidPhysicalMouseCapture` from `CameraRotation.cs`, `Helper.cs`, `MouseLook.cs`, `ThirdPerson.cs`, `NavigationCamera.cs`. Current source class exists under `android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs` but is wrapped in `#if UNITY_ANDROID && !UNITY_EDITOR`, making it unavailable to Editor assembly when caller references are compiled. The native workflow explicitly stages this .cs, so likely defines/conditional compilation mismatch rather than missing copy. This is a **probable, source-supported root cause**, not a patch or verified rerun. T4 owns mouse source, T5 owns native build; did not edit or launch them. Upstream script compile prevents an FFT-on-device conclusion.

## Next independent T1 action

After T4/T5 integrate and prove native compile fix or in a separate authorized Unity runner, use pinned ZIP2 actual original and original-vs-Unity physical *same-input* keyed invocations and shader/kernel/texture/dispatch evidence. The added producer-stage checks now fail closed on swapped or incomplete private captures. Only a genuine original-vs-Unity numeric/pixel difference and authored in-game binding can justify smallest semantics-preserving FFT shader patch and later a phone test; original ZIP2 binary and Android Adreno have **not** been executed this cycle. Maintain T1 vote **لا يحتاج**, no fake READY or audio/Settings regression.
