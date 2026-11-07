# T2 WATER-001 scope — 2026-11-07T13:21Z
session_id: 20261107T1321Z-T2-scheduled-budget-guard-r6v3
origin: scheduled
issue_id: WATER-001
baseline_sha: eca2cda7f651b5f4f8d29f4af03a9c8be85698ee
status: active
intended_files: scripts/t2_pass1_stack_provenance.py; tests/test_t2_pass1_stack_provenance.py; own session/work files
experiment_key: synthetic-IL-budget-cap-128-existing-trace-eca2cda7
resource_key: none
hypothesis: max_steps >128 bypasses intended synthetic straight-line instruction budget. Reject values >128 without altering legitimate <=128 behavior.
resumed_from: 20261107T1120Z-T2-scheduled-reconstructed-suite-r9k4 and previous patch prepared in scheduled cycle.
Constraints: no original-game parser, shader, Unity or device claims; coordinate with T1/T3 water and effects, no shared file edits.
Owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (phone world save/reentry succeeded, water/FFT still broken).
