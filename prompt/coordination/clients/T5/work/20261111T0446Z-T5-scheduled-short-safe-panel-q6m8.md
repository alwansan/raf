# T5 scope — 20261111T0446Z-T5-scheduled-short-safe-panel-q6m8
origin=scheduled
baseline_sha=623a8c4c449f01fb31394ea04e9a1c80ecc42d35
track=DISPLAY-003
scope=AndroidTouchUiPanel report/editor responsive safe-area geometry only; no T4 mouse, no Unity shared workflow, no gameplay touch redesign.
Hypothesis: current Panel() fixes top offset 228 and report height 440 in 720-unit reference canvas, clipping below bottom on safe areas under 668 UI units; adjust scale to fit while preserving 720 layout.
Experiment key=T5-SAFE-PANEL-20261111-Q6M8
Shared resource=none; CI=none until source tests inspected; owner source screenshot pending.
Previous evidence: 20261110T0352Z-T5-scheduled-safearea-a9c7.md proves three right-side buttons already anchored to safe area; do not duplicate.
