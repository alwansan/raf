# T1 WATER-001 — bounded Android GPU compute mini-lab
session_id: 20261108T1538Z-T1-chat-gles31-probe-7e4a
origin: chat
issue_id: WATER-001
base_sha: 77837352fb8855c1c81c985dca951d3d2941a7c1
resumed_from_sessions: clients/T1/sessions/20261108T1506Z-T1-scheduled-trace-ci-8f2c.md; prompt/coordination/clients/T1/sessions/20261108T1410Z-T1-scheduled-trace-mutation-c9e4.md
status: active
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
