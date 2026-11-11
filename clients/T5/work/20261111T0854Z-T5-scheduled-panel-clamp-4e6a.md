# T5 scoped work — 2026-11-11T08:54Z
session_id: 20261111T0854Z-T5-scheduled-4e6a
origin: scheduled
baseline_head: 0eb7c5f37ce2279445a5b94c5033e3901fc44d53
scope: android-port/Runtime/Platform/AndroidTouchUiPanel.cs (FitPanelsToSafeArea only); scripts/tests/test_t5_panel_safe_geometry.py (new); own session file.
hypothesis: the panel's positive 0.1 minimum scale overflows tiny Screen.safeArea while three right buttons correctly use Clamp01. Fix panel clamp, preserving original panel geometry/Settings and gameplay controls.
experiment_key: T5-PANEL-SAFE-CLAMP-20261111
shared_resource: none; no Unity/CI dispatch. T4 owns physical mouse; do not touch mouse code.
taken_over_from: T5 width-safe 85fc2a2076b95f5f7b9757cafc029d1f232d56ee and height-panel 6e0a33decf464afdc9f988019d6ae63d260a03f5.
status: PLANNED
