# T4 INPUT-005 — reset-epoch evidence integrity
session_id: 20261111T2340Z-T4-scheduled-r6m8
origin: scheduled
baseline_sha: c9db87e742577461a315da9d5e0b5685c5fab969
scope: scripts/t4_capture_gap_classifier.py; tests/test_t4_capture_gap_classifier.py; this work and isolated session.
Hypothesis: when reset counters are positive, classifier returns unvalidated growth values (negative/bool/string), despite labeling reset segmentation required. This leaks malformed evidence into downstream automation. Sanitize each growth value to None unless nonnegative exact integer, while retaining conservative reset state. Add regression tests.
No Unity build, no changes to .rgd, keyboard, T5 resolution/layout or shared assets. Resource: Python source only; no shared Unity/CI allocation.
Owner phone evidence: 42058825739 local world/save/reload succeeded; publication failed separately. No phone proof of captured clicks. CL 520c4cf evidence is historical and not a same-build capture proof.
Prior T4: 20261111T2037Z-T4-scheduled-mouse-proof-c7r9 and later 20261111T2230 approximate CLI regression work; avoid repeating gameplay claims.
