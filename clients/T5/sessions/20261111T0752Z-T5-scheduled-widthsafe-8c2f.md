# T5 scheduled checkpoint — 20261111T0752Z-T5-scheduled-widthsafe-8c2f
origin: scheduled
session_id: 20261111T0752Z-T5-scheduled-widthsafe-8c2f
resumed_from_sessions: prior T5 scheduled result 8d05dfc6d1132651148f94777f9b0bc70cc0e8a5
scope: clients/T5/work/20261111T0752Z-T5-scheduled-widthsafe-8c2f.md
source_file: android-port/Runtime/Platform/AndroidTouchUiPanel.cs
source_blob_before: 5d268e4d80b613f8cbdbb32f88c2b5996c1ad556
plan_commit: 246fad1bcbaaee0d5965ef49b38556af9a51b396
fix_commit: 85fc2a2076b95f5f7b9757cafc029d1f232d56ee
test_commit: 84d72a0be3cfe382de32d2b663eda5779cf3ce7f
origin_device_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (owner world/save/reload only)

## Finding
Prior height-only scaling of three top-right diagnostic buttons could overflow the left edge when Screen.safeArea is narrow. Clamp scale by both safe-area width and height in CanvasScaler height units, preserving right alignment, original offsets and three actions. No changes to T4 mouse handling, gameplay touch, saves, FMOD or Unity resources.

## Verification and limits
Six width/height scenarios passed CPU geometry assertions. Source-level regression added in scripts/tests/test_t5_right_buttons_safe_width.py. No new CI, Unity compilation, device FPS or signed APK/OBB evidence. Device READY remains NOT_READY; prior LogRaft 22.29 displayed-frame estimate is not GPU time.

## Next
Execute regression on runner, inspect existing Resolution settings for a non-overlapping source fix, then confirm on real Android safe areas. Verify signed APK/OBB SHA and versionCode only from actual signed bytes. Do not duplicate running Unity jobs.
