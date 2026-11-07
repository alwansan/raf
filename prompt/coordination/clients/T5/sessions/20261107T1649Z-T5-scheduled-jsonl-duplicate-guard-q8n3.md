# 20261107T1649Z-T5-scheduled-jsonl-duplicate-guard-q8n3
origin: scheduled
role: T5
baseline_sha: 5b4c0aaf65c8334ee53fe15879293064819ed036
resumed_from_sessions:
- 20261107T1552Z-T5-scheduled-unity-epoch-p7n4
- 20261107T1453Z-T5-scheduled-unity-refresh-epoch-r6q2
scope: prompt/coordination/work/PERF-007/20261107T1649Z-T5-scheduled-jsonl-duplicate-guard-q8n3.json
scope_commit: ebf05ef0f3c6441cbb8237c2e4c6680f781230d1
code_commit: 9d06e0a1880e944740f63ce05781b4b2d6ff2d10
test_commit: 3983a081ebe94507c84caf8015934e9a9c5a66f2
work_checkpoint: 7b3407ddbaaed46d91bb9af730907b3c299dcbdd

## Result
Read owner phone feedback, current team coordination and trial votes; confirmed original phone world/save/reentry on source e9c358ed is limited to run42058825739. Latest inspected branch HEAD before scope 5b4c0aaf. Continued T5 interval analyzer without touching T4 mouse, Unity, shared native request or other clients' files.

Fixed Python json.loads default duplicate-key acceptance in scripts/t5_unity_interval_epoch.py by strict object_pairs_hook; rejects ambiguous keys in top-level or nested JSONL. Added 3 regression tests in tests/test_t5_unity_interval_epoch.py (top-level duplicate, nested duplicate, valid distinct keys). Source code committed, but **full tests/CI and original CL-schema compatibility remain unverified**; do not report green. No device metrics, APK/OBB binary matching or Resolution behavior proof. Work status waiting_ci. Avoid duplicate native Actions; trial vote still not 5/5 and owner-direct build is a separate exception.

## Next
Run python3 -m unittest tests.test_t5_unity_interval_epoch and inspect CI after commit 3983a08. Compare parser against original pinned CL log with bounded read, repair schema mismatch if present; then attach APK/OBB identity before cross-build performance comparisons. Coordinate Resolution changes with live HEAD and T4 mouse scope. Game NOT_READY 0/3.
