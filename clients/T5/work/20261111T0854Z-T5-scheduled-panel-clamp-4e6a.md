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

## Result
status: SOURCE_INTEGRATED_UNTESTED
source_commit: 6da432b4108e2e1934e57b54a0aa29529cd0b36e
test_commit: 18d5d885d5439d1712c484452b2c764ca2958843
verification: source re-read and six analytical geometry cases; no Unity compile, no device evidence, no FPS claim.
next: execute scripts/tests/test_t5_panel_safe_geometry.py on CI or Python runner; test Android safe areas; continue Resolution settings investigation and signed APK/OBB SHA provenance.
