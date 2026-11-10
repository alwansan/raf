# T1 scoped work — 20261110T0310Z-scheduled-native-group-validation-c7a2
origin: scheduled
baseline_sha: 443da13323a40b83fc358b355ea1f4fdd97051f1
issue: WATER-001
files: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_dispatch_group_validation.py; own session
experiment_key: T1-native-fft-group-positive-20261110
shared_resource: none; no Unity/APK/CI manual dispatch
hypothesis: Native before-dispatch trace currently accepts zero or negative Y dispatch group count, permitting an invalid call to be treated as an admissible pair. Validate Y>0 and all numeric source arguments nonnegative where justified; preserve legacy traces and evidence boundary.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; original game world save/reentry success from artifact, water errors remain.
coordination: T4 mouse and T5 resolution/packaging untouched. Previous T1 chat synchronous throw hook remains unchanged.
