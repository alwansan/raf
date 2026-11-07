# 20261107T1552Z-T5-scheduled-unity-epoch-p7n4
origin: scheduled
owner: T5
baseline_sha: 5a60dc49c809ec93bc445ec0fc0e36692153fed6
scope: scripts/t5_unity_interval_epoch.py; tests/test_t5_unity_interval_epoch.py; own session file only
hypothesis: Unity-internal FPS samples must never be pooled across scene or refresh-rate epochs, and interval p95 is not pooled frame p95.
experiment_key: PERF-007-unity-interval-epoch-20261107T1552Z-T5-scheduled-unity-epoch-p7n4
shared_resource: none; no Unity/CI requested
previous: prompt/coordination/clients/T5/sessions/20261107T1453Z-T5-scheduled-unity-refresh-epoch-r6q2.md
owner_report: docs/DEVICE_FEEDBACK_42058825739_AR.md
non_overlap: T4 physical mouse, T1/T2 water, T3 materials untouched.
