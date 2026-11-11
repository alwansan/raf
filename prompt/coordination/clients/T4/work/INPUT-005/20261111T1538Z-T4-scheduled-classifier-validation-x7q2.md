# T4 INPUT-005 — counter integrity validation

session_id: 20261111T1538Z-T4-scheduled-x7q2
origin: scheduled
baseline_sha: eea74b7c1142ce7ce823047fd02f335443f8dd8e
scope: scripts/t4_capture_gap_classifier.py and tests/test_t4_capture_gap_classifier.py only; independent of T5 resolution and layout.
hypothesis: malformed/negative/non-numeric growth can be misclassified as real callback or reader growth; conservative classification must reject invalid counters and avoid false causal evidence.
experiment_key: INPUT-005-counter-integrity-x7q2
shared_resource: none; Python source-only, no Unity build.
owner_phone_baseline: Artifact 42058825739 world entry/save/reopen confirmed only for that build; INPUT-005 remains OPEN.
next: add validation and regression tests, verify without modifying keyboard, .rgd, Settings or audio.
