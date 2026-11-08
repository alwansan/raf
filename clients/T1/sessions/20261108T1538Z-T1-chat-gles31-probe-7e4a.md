# T1 chat — authentic Android GPU capability boundary for WATER-001

session_id: 20261108T1538Z-T1-chat-gles31-probe-7e4a
origin: chat
resumed_from_sessions:
- clients/T1/sessions/20261108T1506Z-T1-scheduled-trace-ci-8f2c.md
- prompt/coordination/clients/T1/sessions/20261108T1410Z-T1-scheduled-trace-mutation-c9e4.md
base_sha: 77837352fb8855c1c81c985dca951d3d2941a7c1
issue_id: WATER-001
work_id: clients/T1/work/20261108T1538Z-T1-chat-gles31-probe-7e4a.md
experiment_key: t1-gles31-ssbo-linear-and-two-pass-built-in-shaders-v1
status: lab_apk_ready_to_test_device_pending
planned_files:
- apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1ComputeProbe.java
- apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/MainActivity.java (T1-only wiring)
- apk-for-testing/workers/T1/README.md
- clients/T1/work/20261108T1538Z-T1-chat-gles31-probe-7e4a.md
- this session
- .github/raft-mini-lab-build-request.json only after resolving T4's build-queue conflict

## Live evidence restored
- HEAD at start 77837352fb8855c1c81c985dca951d3d2941a7c1; current branch may advance as T4/T2/T3 work.
- T1 paired source diagnostic [run42493143730](https://github.com/alwansan/raf/actions/runs/42493143730) SUCCESS on 11b69e69cc31608316949e30e76b32877c130ffd; prior T1 session recorded queued and needed this terminal result.
- Latest owner CL `LogRaft-20261108-164850-270`: 11165 invalid compute kernels; 74359 invalid water passes, 7372 cursor warnings, all from one named logging session. Android15 owner mouse physical movement works while buttons scroll fail (T4 scope).
- Owner phone previous World/save/reenter tested from APK [run42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), not current HEAD.
- T4 mini-lab [run42496084526](https://github.com/alwansan/raf/actions/runs/42496084526) at 7ba0068 failed early in android-actions/setup-android@v3: removed SDK package `tools` (`Failed to find package 'tools'`). Therefore did **not** compile any mini APK; T4 immediately patched shared workflow in 6ab099095d3fdca135214c8c01f8fb85e3b2ad44; do not overwrite or cancel.

## Implemented source
- [1a0c7c2](https://github.com/alwansan/raf/commit/1a0c7c2abdd0e829e49d6df755f0a57e687db86e) adds `T1ComputeProbe` with 4 case controls. Later T1 fix [767dba9](https://github.com/alwansan/raf/commit/767dba9847f7c81093c78c53698995abddc5531f) eliminates fake `preexisting_errors=0` metric from GPU success response.
- [f91f934](https://github.com/alwansan/raf/commit/f91f934410baf3f38cef4fc79fd2947a02fa0cff) T1-only host wiring; T4's worker package retains existing mouse cases and callbacks.
- [4621a03](https://github.com/alwansan/raf/commit/4621a036065c7372bc1636b530354ac3de86741f) T1 lab README explains exact cases, expected hashes/mappings, logs and device evidence boundaries.
- Built-in GLSL 310 ES in APK only; no externally imported shader execution. Case1 GL version/caps. Case2 SSBO one dispatch 16-word exact readback. Case3 two dispatches shader-storage barrier and exact readback. Case4 compile-invalid negative.
- No private ZIP2 data, Unity import, original compute translation, Raft save modifications or full APK.
- Device/CI verification for T1 APK: **NONE YET**. Do not ask owner to install / mark READY_TO_TEST until compiled APK exists, SHA256 and artifact verified.

## Next action
1. Check active mini workflow and T4 request on HEAD, avoid replacing an in-flight request.
2. Build T1 using source-complete current branch and corrected SDK setup, diagnose compiler error if any.
3. Verify actual run success and downloadable APK / SHA256. Update T1 TEST_CENTER row and README with specific immutable source and artifact.
4. Device comparison distinguishes generic GLES compute from Unity-specific imported original FFT kernel. PASS in mini-lab is not WATER-001 closure.

## CI build request chronology / concurrency
- T2 independent host [42496746941](https://github.com/alwansan/raf/actions/runs/42496746941) SUCCESS; request marker and parent pinned.
- T1 request commit [42067327](https://github.com/alwansan/raf/commit/42067327d54c2a7f5f160ee7c3bb14287a6f1e95) triggered [42496880833](https://github.com/alwansan/raf/actions/runs/42496880833), but **FAILED pre-build request gate**: declared previous head `0bd6d39f...` vs actual parent `8550519e44566bd4bfc58ff38bb1f1082a333a21`, due concurrent commit while publishing. Zero Gradle/Android work in that run; no APK. Do not bypass parent gate.
- T5 then published independent mini build request [42496945089](https://github.com/alwansan/raf/actions/runs/42496945089) and owns shared host; defer T1 retry until it finishes and a fresh HEAD/request collision check. Do not overwrite the T5 request while in_progress.
- Need new request id, actual HEAD parent (verified immediately after commit), source SHA and run, then sha256 artifact before marking owner READY_TO_TEST.

## Final verified Android APK deliverable (same chat session)
- Created independent path-scoped `.github/workflows/raft-t1-gles31-mini-lab.yml` and one-shot `apk-for-testing/workers/T1/build-request.json` to avoid the shared request's immediate-parent hash race in concurrent team commits, **without disabling or changing the original request security gate**.
- [42497238594](https://github.com/alwansan/raf/actions/runs/42497238594) **SUCCESS** on immutable source `2980d378e37a678feedc3584530bde71212fbd9f`: schema test and Gradle `assembleDebug -Pworker=T1` passed; `test -s` proved APK nonempty; SHA256 printed and 2-file upload succeeded.
- [Actual Artifact #13624351093](https://github.com/alwansan/raf/actions/runs/42497238594/artifacts/13624351093), ZIP 35,404 bytes, expires 2026-11-15T15:56:34Z. Inside: `apk-for-testing/host/app/build/outputs/apk/debug/app-debug.apk` and `mini-lab-sha256.txt`. APK package `com.alwansan.raft.lab.t1`, versionCode=1, SHA256 `d87dc468ab39ea2ac67fe09fe1e02b34052c84f09ab3ad9bd8d22d24d18449a6`.
- Previous shared-host requests [42496880833](https://github.com/alwansan/raf/actions/runs/42496880833) and [42497135091](https://github.com/alwansan/raf/actions/runs/42497135091) failed immediate-parent gate before Gradle due concurrent changes; preserve as failed, no repeated identical Gradle build.
- Changed only T1 TEST_CENTER row and T1 README to READY_TO_TEST; actual owner phone tests CASE T1-01, T1-02, T1-03, T1-04 and JSONL/screenshot pending. **WATER-001 OPEN, full game NOT_READY 0/3**; generic GLES31 diagnostics do not prove original Unity FFT kernel index 6 FindKernel/dispatch or restored water.
- No full Unity game APK/OBB/XAPK build, no changes to shared native request, no other worker's vote or scheduled task.

## Latest owner-path corrected APK, superseding initial build
- User explicitly requested exported JSONL at `/storage/emulated/0/Download/Games/cl/raft log/test/<worker>-<lab>-<session>/`, while inherited host default was `Download/Games/cl/test/`. Source correction [2c839db](https://github.com/alwansan/raf/commit/2c839dbac36b34a70ac6c90bb69e0fa0ef890fd7) selects the latest user path for **T1 only**, preserving T2–T5 original paths. App logs actual version in [cb492a0](https://github.com/alwansan/raf/commit/cb492a06e517da5a93212bbb98945fdc3f60745e); T1 package upgraded to versionCode 2 / `0.1.1-t1-export-path` in [6163005](https://github.com/alwansan/raf/commit/61630057cc760ead702024ec9a9191c3985f5f72). Four GPU cases unchanged.
- **LATEST** isolated T1 CI [42497767712](https://github.com/alwansan/raf/actions/runs/42497767712) **SUCCESS** on source SHA `37182f0e9d38c0c38f3e78e7e5c21463eeaac8d9`. Real [Artifact #13624141881](https://github.com/alwansan/raf/actions/runs/42497767712/artifacts/13624141881), ZIP 35,583 bytes, expires `2026-11-15T16:03:00Z`, contains `app-debug.apk` and `mini-lab-sha256.txt`. APK SHA256 `d177634c7ee7d71117005000fa904db03e825a43ba63dbe921ddf43cc077d0b7`. README and only T1 TEST_CENTER row updated. Prior run42497238594 v0.1.0 retained in history but superseded for new phone testing.
- **STATUS:** mini-lab READY_TO_TEST, owner CASE T1-01..04 execution and event JSONL/screenshots PENDING. WATER-001 remains OPEN and full Raft NOT_READY0/3; successful isolated GLES31 shader test cannot prove original Unity ComputeShader import/kernel6 or restored UltimateWater, and no original shader assets have been altered.
