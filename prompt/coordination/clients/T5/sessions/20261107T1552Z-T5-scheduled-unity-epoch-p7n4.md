# 20261107T1552Z-T5-scheduled-unity-epoch-p7n4
origin: scheduled
role: T5
baseline_sha: 5a60dc49c809ec93bc445ec0fc0e36692153fed6
scope_commit: 97b20457b66271cea667bd5a3051ad68e2e16be8
code_commit: eb004ce007d7e054c921c54a7c900d86fe03a689
test_commit: 6970c1dbbff89ec4187b132ad86cf611cab7db14
previous: 20261107T1453Z-T5-scheduled-unity-refresh-epoch-r6q2
origin_report: docs/DEVICE_FEEDBACK_42058825739_AR.md

Added scripts/t5_unity_interval_epoch.py and tests/test_t5_unity_interval_epoch.py to fail closed on missing/invalid Unity interval metrics, duplicate detail keys, and to separate contiguous scene/refresh/window-resolution epochs. Startup intervals <30 frames excluded; median interval FPS and median interval p95 explicitly not pooled per-frame quantiles. Read-only; no private CL raw data committed.

Validation boundary: seven regression test cases committed but no test-run/CI result yet; no new device or GPU measurement. The source parser expects area=performance operation=sample and semicolon key=value detail. Confirm against pinned original CL JSONL before claiming real-session metrics; do not conflate SurfaceFlinger, Unity and GPU. Third CL file still requires bounded read. No APK/OBB binary matching claimed. No Unity build requested; trial votes are not unanimous. T4 mouse untouched.

Next: run python3 -m unittest tests.test_t5_unity_interval_epoch and test against pinned original CL log. If schema differs, correct parser with original evidence; add identity gates for signed APK/OBB before any cross-build comparison. Keep Resolution and UI non-regression work separate.
