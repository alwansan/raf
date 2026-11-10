# T2 scoped work — 20261110T2122Z-T2-scheduled-utf8-fixture-v8n2
session_id: 20261110T2122Z-T2-scheduled-utf8-fixture-v8n2
origin: scheduled
issue_id: WATER-001
baseline_sha: b026998095caf9dd918b6bc060c7c3a196ba17fb
status: active
experiment_key: t2-foam-cli-utf8-invalid-byte-fixture-v1
resource_key: none; source-only Python regression
intended_files: tests/test_t2_foam_evidence_cli_integration.py; prompt/coordination/clients/T2/sessions/20261110T2122Z-T2-scheduled-utf8-fixture-v8n2.md; this work file
hypothesis: The existing test_invalid_utf8_is_rejected uses b"\\\\xff", which is ASCII literal backslash-x-f-f rather than byte 0xff, and therefore can pass for JSON syntax rejection without exercising UTF-8 decoding. Replace with a genuinely invalid byte, add explicit valid UTF-8 malformed-JSON control, retain fail-closed stdout assertions.
owner_baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; world save/reentry owner confirmed; WATER-001 open.
resumed_from: clients/T2/sessions/20261110T1923Z-T2-scheduled-evidence-cli-ci-q8v4.md
boundary: no original shader recovery, Unity, Android or publisher integration claimed.
