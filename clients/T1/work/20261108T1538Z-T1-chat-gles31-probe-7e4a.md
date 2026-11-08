# T1 WATER-001 — bounded Android GPU compute mini-lab
session_id: 20261108T1538Z-T1-chat-gles31-probe-7e4a
origin: chat
issue_id: WATER-001
base_sha: 77837352fb8855c1c81c985dca951d3d2941a7c1
resumed_from_sessions: clients/T1/sessions/20261108T1506Z-T1-scheduled-trace-ci-8f2c.md; prompt/coordination/clients/T1/sessions/20261108T1410Z-T1-scheduled-trace-mutation-c9e4.md
status: source_ci_complete_device_test_pending
scope: Android 15 GLES 3.1 compute capability + SSBO dispatch/readback positive/negative controls; no private Raft shader/source, no Unity
intended_files: apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1ComputeProbe.java; bounded T1-only branch of MainActivity.java; apk-for-testing/workers/T1/README.md; clients/T1/sessions/20261108T1538Z-T1-chat-gles31-probe-7e4a.md; clients/T1/work/20261108T1538Z-T1-chat-gles31-probe-7e4a.md; .github/raft-mini-lab-build-request.json only after source validation
experiment_key: t1-gles31-ssbo-linear-and-two-pass-built-in-shaders-v1
resource_key: mini-lab-host-android-build-optional; no full Unity build
observed_owner: CL/raft log/lf/LogRaft-20261108-164850-270 11165 water_fft_invalid_compute_kernel; 74359 ultimate_water_invalid_pass (single session)
current_ci: T1 paired FFT CI 42493143730 success on 11b69e69cc31608316949e30e76b32877c130ffd
collision_check: no in_progress Actions at check; T5 latest scoped work source-only CI provenance, T4 INPUT-005. Modify common MainActivity minimally and re-fetch current blob before update. No duplicate heavy CI.
hypothesis: Distinguish Adreno OpenGL ES 3.1 general compute dispatch/SSBO vs unavailable compute, without claiming original Unity FindKernel or original water shader support.
negative_control: deliberately invalid compute GLSL must be rejected by compiler. Positive controls require exact CPU-known output readback, not just GL_NO_ERROR.
acceptance: a signed mini APK must be built and hash/Artifact URL verified before owner is invited to test. Until then SOURCE_READY, not READY_TO_TEST.

## 2026-11-08 update — compile validation and shared request collision
- T1 compile defect in run [42496449259](https://github.com/alwansan/raf/actions/runs/42496449259) (Javac definite assignment of final observation) fixed in [ae450f1](https://github.com/alwansan/raf/commit/ae450f1f84ef4956f577df29cb21214517a8f065).
- T4 mini host [42496622364](https://github.com/alwansan/raf/actions/runs/42496622364) subsequently **SUCCESS** including shared Java source; artifact belongs to worker **T4**, not T1. T1 GPU tests remain unexecuted on device.
- Attempted T1 build request with expected blob SHA was rejected 409: concurrent T2 updated `.github/raft-mini-lab-build-request.json` on 1eb3e880e65a6f239be9b3cfbe1ff761851091eb and started [42496746941](https://github.com/alwansan/raf/actions/runs/42496746941). **Respected conflict; do not override T2 request or duplicate queued build**. Recheck live Actions/request after T2 completes; only then dispatch one T1 build using fresh HEAD parent.
status: build_complete_device_test_pending

## 2026-11-08 final source+CI milestone
- T1 mini test source, host integration, T1-only independent workflow and one-shot trigger BUILT successfully: [run42497238594](https://github.com/alwansan/raf/actions/runs/42497238594), source `2980d378e37a678feedc3584530bde71212fbd9f`, real [artifact13624351093](https://github.com/alwansan/raf/actions/runs/42497238594/artifacts/13624351093) ZIP 35404 bytes, expires 2026-11-15 15:56Z. APK SHA256 `d87dc468ab39ea2ac67fe09fe1e02b34052c84f09ab3ad9bd8d22d24d18449a6`, package `com.alwansan.raft.lab.t1`, versionCode 1.
- Expected owner results: four CASEs `T1-01..T1-04` on Adreno730 should PASS if generic ES3.1 compute works. Request exported JSONL and screenshot of unexpected cases. No phone results yet, no original Unity GPU/FFT parity.
- Updated T1-only test center row, T1 README, T1 MEMORY and chat session. No common build/voting modifications. Root `WATER-001` OPEN, full game NOT_READY0/3; continue authenticated original kernel mapping and real Raft integration separately.

## Superseding the initial lab artifact with owner-requested log folder
- Latest T1 source-only changes: MainActivity T1 export relative path `Download/Games/cl/raft log/test/`, app version logged, Gradle T1-only versionCode2; T2–T5 not redirected. Single T1-only path-scoped test trigger produced [42497767712](https://github.com/alwansan/raf/actions/runs/42497767712) **SUCCESS**.
- Immutable tested source: `37182f0e9d38c0c38f3e78e7e5c21463eeaac8d9`; artifact [#13624141881](https://github.com/alwansan/raf/actions/runs/42497767712/artifacts/13624141881), ZIP 35,583 bytes, expiry `2026-11-15T16:03:00Z`; package `com.alwansan.raft.lab.t1`, v`0.1.1-t1-export-path`, versionCode2; APK SHA256 `d177634c7ee7d71117005000fa904db03e825a43ba63dbe921ddf43cc077d0b7`.
- Prior run42497238594 v0.1.0 still documented as historical, **superseded**; device feedback pending and no Raft full acceptance. Final source-and-CI scope complete, no full Unity build or T-team voting changes.
