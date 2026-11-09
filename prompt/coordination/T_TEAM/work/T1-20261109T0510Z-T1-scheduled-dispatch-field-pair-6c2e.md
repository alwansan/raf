# T1 WATER-001 isolated scope
session_id: 20261109T0510Z-T1-scheduled-dispatch-field-pair-6c2e
origin: scheduled
baseline_sha: 50faa92289c6a0c05ec0a3ddfcb440d675b05950
experiment_key: T1-FFT-DISPATCH-FIELD-PAIR-20261109
files: scripts/t1_fft_dispatch_pair_audit.py; scripts/test_t1_fft_dispatch_pair_identity.py; clients/T1/sessions/20261109T0510Z-T1-scheduled-dispatch-field-pair-6c2e.md
hypothesis: sequence-only pairing permits contradictory dispatch metadata. Compare common metadata without claiming GPU execution.
shared_resource: none; no Unity or APK launch.
evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md
scope: isolated T1 Python audit, no T4/T5 files.
