# T2 scope — 20261110T1724Z-T2-scheduled-cli-boundary-p6k8
origin: scheduled
baseline_sha: 7d90f989b6d8e1b7432c9497a9146b0f5a7cb68a
issue: WATER-001 / evidence publication boundary
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md (run 42058825739, CL 520c4cf)
taken_over_from: clients/T2/sessions/20261110T1518Z-T2-scheduled-flag-integrity-n5q2.md
hypothesis: Python parser unit tests do not establish that the executable CLI returns no sanitized JSON on invalid input. Test the actual subprocess interface before treating it as a safe CI evidence producer.
scope_files: tests/test_t2_foam_evidence_cli_integration.py; this work file; own session file only.
experiment_key: T2-EVIDENCE-CLI-BOUNDARY-20261110
shared_resources: none; no Unity, no Android build, no Actions dispatch.
non_goals: No claim of original Foam texture/CB name binding, ShaderLab readiness, or device pixels. T3/T4/T5 files untouched.
expected_sha_policy: reread branch HEAD before publishing source; no force.
