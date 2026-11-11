# T5 right controls short-safe-area correction
session_id: 20261111T0548Z-T5-scheduled-rightbuttons-r6k2
origin: scheduled
issue_id: DISPLAY-003
base_sha: 09c14c720cbde14e89e10aa1d0a89ed2c8ade1a6
status: completed_source_patch; unity_and_device_unverified
intended_files: android-port/Runtime/Platform/AndroidTouchUiPanel.cs; independent session and experiment files
hypothesis: right-aligned three diagnostic buttons currently retain fixed y positions and extend outside short Android safe areas even after recent editor/report panel scaling.
experiment_key: t5-right-buttons-safe-height-source-09c14c7
resource_key: none; no Unity shared build
coordination: T4 owns physical mouse; no T4 source edits. Previous panel scaling 6e0a33d preserved.

## Result
- Source correction: abb586df2ccf912aed661448ff16eea06f928d22
- Regression: 3708ea10df4fcacb9ca016f93f0bacac7ca5e8b0
- Preserves existing right anchors, rescales three actions only when safe area shorter than 224 Canvas units; no gamepad or T4 mouse source touched.
- Static geometry and source contract added in tests/test_t5_right_diagnostic_safe_area.py; no Unity/device evidence.
- Next: execute test in CI/locally, validate screenshot on phone, then work on existing Settings Resolution binding and signed APK/OBB.
