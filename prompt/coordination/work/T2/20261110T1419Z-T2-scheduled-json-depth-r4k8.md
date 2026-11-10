# T2 scoped work — 2026-11-10T14:19Z
session_id: 20261110T1419Z-T2-scheduled-json-depth-r4k8
origin: scheduled
issue_id: WATER-001
base_sha: 0e7d5cbb66440750444cc5a4295199ea7be014c5
status: active
intended_files: scripts/t2_foam_evidence_gate_20261110.py; tests/test_t2_foam_evidence_gate_20261110.py; this work; own session
experiment_key: foam-aggregate-json-nesting-recursion-python-json-64KiB-20261110
resource_key: none (source-only)
hypothesis: a JSON array nested below 64KiB triggers RecursionError outside EvidenceError, bypassing fail-closed report parser and CLI.
method: add explicit RecursionError normalization and adversarial regression; run local Python test on exact fetched files; no original game resources, no CI or Unity.
owner baseline: DEVICE_FEEDBACK_42058825739_AR.md, CL 520c4cf4, world save/reopen success; WATER-001 remains OPEN, NOT_READY 0/3.
coordination: T3 FX, T4 physical mouse, T5 Resolution/shared APK untouched.
