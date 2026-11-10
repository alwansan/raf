# T2 WATER-001 — evidence producer integration boundary
session_id: 20261110T1617Z-T2-scheduled-producer-boundary-v8n3
origin: scheduled
base_sha: 2b1bf7eaa0e8f472c594797d450d8bf2a7514ff4
issue: WATER-001 OPEN / NOT_READY 0/3
scope: audit only scripts/t2_foam_evidence_gate_20261110.py and tests/test_t2_foam_evidence_gate_20261110.py; independent of T1/T3/T4/T5 source.
experiment_key: T2-FOAM-PRODUCER-BOUNDARY-20261110
hypothesis: existing strict JSON parser is standalone, not demonstrated as a mandatory gate at actual report producer or upload boundary.
Evidence: source parser defines parse_aggregate_json and CLI main; test suite exercises parser and sanitize directly. No actual producer invocation or CI upload-path proof established by these two files. A green unit test alone cannot establish that production artifact publication invokes the sanitizer.
Next: identify exact producing workflow and upload step, then fail-closed validate aggregate JSON immediately before artifact upload; add integration test with sanitized fixture and rejected raw payload. Do not claim production integration before proving invocation.
Owner device: 42058825739 world/save/re-entry PASS; 220911-559 23884 water-pass errors and 3850 FFT errors. 8-Nov shared mini lab supersedes separate mini APK plan. No build, no shared resource reserved.
