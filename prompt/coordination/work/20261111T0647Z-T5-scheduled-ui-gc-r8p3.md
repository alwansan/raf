# T5 scope / 2026-11-11T06:47Z
session_id: 20261111T0647Z-T5-scheduled-ui-gc-r8p3
origin: scheduled
base_sha: d9f2b6a325d31d58d2e2136997a2dc6afa1fac7b
issue: UI / performance (owner 42058825739)
files: android-port/Runtime/Platform/AndroidTouchUiPanel.cs only, separate session record
hypothesis: FitRightButtonsToSafeArea executes every frame and allocates two arrays and performs three Transform.Find calls per frame. Cache references at creation and static offsets, preserve safe-area geometry.
experiment_key: T5-UI-GC-20261111-r8p3
shared_resource: none (no Unity build or release)
non_overlap: T4 owns mouse; do not touch input files. No touch control redesign. Verify HEAD and file blob before update. Source-only validation, no phone claim.
