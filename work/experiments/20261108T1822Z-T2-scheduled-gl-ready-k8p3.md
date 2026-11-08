# T2 GLES context readiness gate
session_id: 20261108T1822Z-T2-scheduled-gl-ready-k8p3
origin: scheduled
baseline_sha: 67feffde72d6ba7ab7a59244d4f8099840cdd915
branch: feature/android-native-port
scope: apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T2GpuActivity.java only; independent of T1/T3/T4/T5 files.
experiment_key: T2-GLES-CONTEXT-READY-20261108
resource_key: WATER-001 (OPEN)
Hypothesis: shared automatic T2 case starts at fixed 1000ms and may check before GLSurfaceView.onSurfaceCreated, producing false FAIL on slow initialization. Add bounded main-thread readiness polling with timeout, retaining explicit failure on unavailable context; no synthetic PASS.
Evidence: owner 42058825739 phone world/save/reentry success, water/FFT errors remain. T2 source 73924c998d91eb64be33c883d9922d44981accd4 spatial contrast probe, device untested. Shared lab policy requires truthful auto status.
Coordination: T5 owns unified build; no CI dispatch or build. Do not touch shared pack/readiness or original Raft shaders. No competing T2 source edit observed in latest T2 session at 18:17 UTC; recheck blob SHA before write.
Validation: source-level checks and compile gate needed after patch; phone remains unverified.
