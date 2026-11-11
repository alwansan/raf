# T5 width-safe diagnostics scope
session_id: 20261111T0752Z-T5-scheduled-widthsafe-8c2f
origin: scheduled
issue_id: DISPLAY-003
status: active
intended_files: android-port/Runtime/Platform/AndroidTouchUiPanel.cs; scripts/tests/test_t5_right_buttons_safe_width.py
experiment_key: right-three-buttons-width-clamp-v1-source-5d268e4d80b613f8cbdbb32f88c2b5996c1ad556
resource_key: none (no Unity)
updated_at: 2026-11-11T07:52:00Z
hypothesis: Existing three-button fit scales only by safe height; a narrow Android safeArea can clip the left side of the 150-unit buttons even when vertical fit succeeds. Clamp scale by safe width as well; leave T4 mouse files untouched.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md and 5e7a1faa0b13323a269b0e7c8d794b563acf389d.
