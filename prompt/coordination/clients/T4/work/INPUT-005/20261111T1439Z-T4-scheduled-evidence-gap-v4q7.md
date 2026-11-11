# 20261111T1439Z-T4-scheduled-evidence-gap-v4q7
origin=scheduled
baseline_sha=a62b152d2cc37b1600355685388555c2e73b2535
issue=INPUT-005
scope=independent diagnostic classification; no Android/Unity input source edits
files= scripts/t4_capture_gap_classifier.py, tests/test_t4_capture_gap_classifier.py, clients/T4/work/INPUT-005/20261111T1439Z-T4-scheduled-evidence-gap-v4q7.md, clients/T4/sessions/20261111T1439Z-T4-scheduled-evidence-gap-v4q7.md
hypothesis=Aggregate callback and reader counters can be classified conservatively without implying causality or gameplay success. Zero baseline-delta is unknown, not proof of dropped event.
experiment_key=T4-CAPTURE-GAP-20261111-01
shared_resource=none; no Unity or APK CI request
previous=20261111T1337Z-T4-scheduled-zip-log-input-k9r2.md
owner_device=42058825739 world entry/save/exit/re-entry succeeded on device; delivery failed. Keep .rgd and keyboard unchanged. Mouse buttons and scroll remain unconfirmed.
next=implement classifier and regression tests, then compare same-build Android and Unity log with T5.
