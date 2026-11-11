# T5 width-safe diagnostics scope
session_id: 20261111T0752Z-T5-scheduled-widthsafe-8c2f
origin: scheduled
issue_id: DISPLAY-003
status: completed
intended_files: android-port/Runtime/Platform/AndroidTouchUiPanel.cs; scripts/tests/test_t5_right_buttons_safe_width.py
experiment_key: right-three-buttons-width-clamp-v1-source-5d268e4d80b613f8cbdbb32f88c2b5996c1ad556
resource_key: none (no Unity)
updated_at: 2026-11-11T07:52:00Z
hypothesis: Existing three-button fit scales only by safe height; a narrow Android safeArea can clip the left side of the 150-unit buttons even when vertical fit succeeds. Clamp scale by safe width as well; leave T4 mouse files untouched.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md and 5e7a1faa0b13323a269b0e7c8d794b563acf389d.

## Result
Source fix commit 85fc2a2076b95f5f7b9757cafc029d1f232d56ee; CPU regression source commit 84d72a0be3cfe382de32d2b663eda5779cf3ce7f. Six geometric safe-area cases pass locally. Unity compilation/device behavior not verified. No Unity Actions dispatched. T4 mouse scope untouched. Next: run python3 -m unittest scripts/tests/test_t5_right_buttons_safe_width.py in a source CI and validate on-device alongside existing Resolution settings; do not claim FPS gain.
