# T2 scheduled session — 2026-11-08T17:15:38Z
session_id: 20261108T171538Z-T2-scheduled-fbo-audit
origin: scheduled
branch: feature/android-native-port
resumed_from: T2 previous scheduled cycle (T2GpuActivity viewport/async result repair; commits ced6e709, b926f576, 52c5a021); source and policy read live.
base_sha: 9b89f62772c2c61f6269fd2249f8560af1522892 (recent commit search, not independently proven branch HEAD)
scope: T2 shared mini lab FBO audit, no game shader edits.
experiment_key: T2-SHARED-FBO-20261108
resource_key: WATER-001
work: work/experiments/T2-20261108-shared-lab-fbo-audit.md

## Owner/device baseline
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first: 42058825739 artifact allowed world entry, save and re-entry, while publishing APK/OBB/XAPK failed; water/FFT remained broken. Newer 8 Nov owner unified lab policy supersedes five individual APKs. Device log counts in latest policy are session-specific, not proof of GPU root cause.

## Verified source observations
- Unified pack includes T2-01..04, driver t2_gles, mode auto, screenshot none.
- UnifiedLabActivity launches T2GpuActivity with auto_case_id and expects matching case_id/status/observed.
- T2GpuActivity executes real GLES3 controls on GL thread and returns PASS only if observed starts with OK; source includes two-pass FBO pixel check and two negative controls.
- Previous T2 individual APK CI 42496746941 SUCCESS is historical; no proof of unified APK or phone test.
- No original Spectrum/Foam/Blur ShaderLab, CB0 or texture binding verified by these synthetic controls.

## Changes
- Scope record commit 6eac6129368a5b348a6843657886bfee7a60d492.
- T2-only row in SHARED_BUILD_READINESS.md set WAITING_MERGE, commit 27f1de67a7a24c3bab6a53a0687e4971a28c8a55.
- No Unity/native game build, no duplicated mini build or Actions cancellation. No changes to shared pack/renderer code.

## Limitations and next step
No verified full HEAD ref/queued Actions/release enumeration in this cycle; do not claim no runs. T5 should verify manifest/sourceSet and run unified mini CI once integrated. T2 next should inspect original IL pass producers and CB0 mapping with T3, then make a bounded driver change only if warranted. No phone rendering improvement claimed.
