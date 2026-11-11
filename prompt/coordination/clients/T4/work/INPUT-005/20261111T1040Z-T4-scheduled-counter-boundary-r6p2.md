# T4 20261111T1040Z-T4-scheduled-counter-boundary-r6p2
origin=scheduled
baseline_sha=aaf29d6a528e25f313797a24a0a9c0f97b543a80
issue=INPUT-005
experiment=T4-CAPTURE-SUMMARY-COUNTER-BOUNDARY-01

Scope: scripts/t4_capture_reader_summary.py, isolated regression tests and T4-only session. No Unity, keyboard, .rgd, Settings, Resolution, or shared files.

Hypothesis: substring markers and last cumulative snapshot may mislead when last report resets or is truncated. Require exact marker boundaries, preserve last counters for compatibility and expose max counters/reset evidence. No device success inference.

Prior: docs/DEVICE_FEEDBACK_42058825739_AR.md proves world entry/save/reopen on artifact 42058825739. T4 session 20261111T0944Z-T4-scheduled-route-a6k9.md introduced the summary. Mouse clicks remain unverified.

Shared resource: none. No CI/Unity build. Recheck live HEAD before writes.
