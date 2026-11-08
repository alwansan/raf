# T1 chat session — 20261108T1811Z-T1-chat-gles-gate-9d3f

- **origin:** chat
- **identity:** T1, Raft Android T1–T5; write branch: `feature/android-native-port`
- **resumed_from_session:** `20261108T1714Z-T1-scheduled-fft-shared-lab-b6d2` (also reviewed `20261108T1410Z-T1-scheduled-trace-mutation-c9e4`).
- **base_sha:** `7bb7b0452d56f05dbb39d02d400a39729feaa49b`; claim `6d8f2df68b04aa6c072db9777b5bda8293bc29d9`.
- **scope:** synthetic T1-01..04 GLES 3.1 Compute context-startup correctness in one shared Android APK; **not** original Unity FFT restoration.
- **experiment_key:** `t1-shared-gles-context-readiness-v1-20261108`.
- **resource_key:** `T1ComputeProbe.java` only; no T2/T3/T4/T5 code ownership.
- **intended_files:** `apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1ComputeProbe.java`, `tests/test_t1_compute_context_gate.py`, `.github/workflows/raft-t1-shared-compute-source.yml`, this session, own work/experiment/event, T1 MEMORY and T1 shared readiness row.
- **run_urls:** https://github.com/alwansan/raf/actions/runs/42509359669 (source-only compile/testing; do not describe as APK).
- **status:** COMPLETED (source gate), pending T5 Mini build and owner GPU test.

## Live evidence

Live HEAD was `7bb7b0452d56f05dbb39d02d400a39729feaa49b` on 8 Nov 18:11 UTC. At start no active/queued branch Actions. Latest actual Raft owner device-tested game is from Artifacts [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source `e9c358eda01785b65e4eb14f18723da426635628`: world entry/save/reopen worked in limited scenario, publication failed; do not compare this with historical APK86. Latest real Release game android-early-test-41812889049-1 is older; LogRaft-89 is logger, not Raft game. Latest CL 8 Nov LogRaft-20261108-164850-270 counts 74,359 invalid water pass, 11,165 FFT invalid compute kernels and 7,372 cursor RGBA32 messages; counters are session totals, not GPU dispatch proof or render quality metric. Owner hardware Adreno 730 / GLES 3.2, but **this shared APK has not been installed**.

Shared Java host invoked `T1ComputeProbe.runAutomated` after a fixed 1-second UI delay. EGL creation is asynchronous; `GLSurfaceView.queueEvent` can execute while `ready=false`, causing `FAIL no active GLES context` without GPU dispatch. This is a setup race, not measured GPU incompetence. Parent shared app correctly keeps PASS/FAIL explicit; full Unity FFT source/authentic FindKernel mapping still NOT_PROVEN.

## Change and verification

- **Source fix:** `d83a4e4379fb8677daebea81da203281a1d89e82` — bounded 7-second `ready` poll (100 ms), monotonic `SystemClock.elapsedRealtime`; queued GL dispatch only after `onSurfaceCreated`, lifecycle exit protection, timeout logged with **no compute dispatch attempted**, never synthetic PASS.
- **Regression:** `2f26cd2e241a584fbd44d8d9343d2736584fc956` — source contract tests for context ordering, bounded poll, lifecycle, true built-in GPU dispatch and shared bridge. These tests are static source guards, **not EGL/device execution**.
- **Source-only CI:** `695daa697b0ccc0e53ed0533f43b2d267e0036f5` workflow trigger, run [42509359669](https://github.com/alwansan/raf/actions/runs/42509359669). It validates T1 tests and unified pack and compiles shared Java classes, **does not assemble/publish an APK or run GPU on the phone**.
- No changes to Unity, game shaders/assets, T5 build request, native game build marker, other workers' cases or unified pack. No tests claimed to solve original water/shaders.

## Outstanding acceptance

Actual [42509359669](https://github.com/alwansan/raf/actions/runs/42509359669) **SUCCESS** at SHA `695daa697b0ccc0e53ed0533f43b2d267e0036f5`: **5/5** T1 static source contracts and **7/7** unified pack tests, shared Java compile `BUILD SUCCESSFUL in 34s`. T1 has recorded **NEED_BUILD for the shared Mini only** because a compiled T1 driver changed; T5 alone decides whether one shared APK is warranted, checks real signature/source, then delivers one APK via TEST_CENTER. Do not rebuild historical standalone T1 app. No immediate owner action until T5 publishes the actual shared APK. Future device case T1-01..04 results require true Adreno assertions; original Unity water remains WATER-001 OPEN, full game NOT_READY 0/3.

**next_step:** inspect [CI42509359669](https://github.com/alwansan/raf/actions/runs/42509359669); update own shared readiness row, work, experiment/event and memory with exact result; coordinate T5 single Mini build. Keep T1 worker identity and origin in next scheduled/chat cycle.

## Final checkpoint — after source CI

- **Run:** [42509359669](https://github.com/alwansan/raf/actions/runs/42509359669) COMPLETED SUCCESS; one job, all steps passed; pure source/Java compile, zero APK artifacts and no EGL/phone/Unity execution. Source-level tests 5/5, unified pack tests 7/7.
- **T1 shared Mini vote:** NEED_BUILD, only T1 row updated in `apk-for-testing/SHARED_BUILD_READINESS.md` at commit `1d3536f34856491229abe5298738177b5632cd7c`. No vote on full-game XAPK, and T5 build_request untouched.
- **Work:** `prompt/coordination/work/WATER-001/20261108T1811Z-T1-chat-gles-gate-9d3f-shared-context-gate.json` completed; experiment and B_TEAM event recorded by T1. No other worker's source/identity edited.
- **Critical limitation:** root water FFT remains WATER-001 OPEN; no proof `FindKernel`, `Dispatch` or corrected GPU pixels in Raft.
- **next_step:** T5 determine whether a single shared Mini build is now needed and whether one equivalent exists, respecting signing/fingerprint. Then real phone Auto T1 and exported JSONL; independently continue Unity FFT original-source comparison.
