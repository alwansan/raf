# T2 — shared lab FBO audit (2026-11-08 UTC)
origin: scheduled
scope: T2 GLES FBO positive/negative controls in unified APK
baseline: branch feature/android-native-port; current source inspected via GitHub fetch_file
experiment_key: T2-SHARED-FBO-20261108
resource_key: WATER-001
intended_files: this work record; apk-for-testing/SHARED_BUILD_READINESS.md (T2 row only); clients/T2/sessions/20261108T1715Z-T2-scheduled-fbo-audit.md
shared_resource: unified APK integration/build owned by T5; no CI or build requested.

Hypothesis: synthetic GLES3 controls are integrated as source but no verified unified APK/device evidence exists. Audit T2GpuActivity auto case result handling and pack driver linkage, preserve original Raft shader authenticity boundary. Do not edit T5's UnifiedLabActivity or team-testpack.json without coordination.

Baseline owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (world save/re-entry proven, water/FFT still broken); newer unified policy in AGENTS.md supersedes individual mini APK builds.

Checkpoint: T2-01..04 are in unified pack, mapped to t2_gles. UnifiedLabActivity launches T2GpuActivity with auto_case_id; T2GpuActivity runs GL-thread check and returns status from observed prefix OK. Device execution and unified build remain unverified. Historical T2-only APK CI 42496746941 is not the unified APK.

Next: T5 to verify sourceSet packaging, manifest activity, unified build and auto case handshake. T2 to add native driver tests only when a reproducible defect is found; original Foam/Spectrum/Blur binding still needs original IL and CB0 proof.
