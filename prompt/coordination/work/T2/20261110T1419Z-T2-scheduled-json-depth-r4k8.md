# T2 scoped work — 2026-11-10T14:19Z
session_id: 20261110T1419Z-T2-scheduled-json-depth-r4k8
origin: scheduled
issue_id: WATER-001
base_sha: 0e7d5cbb66440750444cc5a4295199ea7be014c5
status: completed_source_change_pending_repo_test
intended_files: scripts/t2_foam_evidence_gate_20261110.py; tests/test_t2_foam_evidence_gate_20261110.py; this work; own session
experiment_key: foam-aggregate-json-nesting-recursion-python-json-64KiB-20261110
resource_key: none (source-only)
hypothesis: a JSON array nested below 64KiB triggers RecursionError outside EvidenceError, bypassing fail-closed report parser and CLI.
method: add explicit RecursionError normalization and adversarial regression; run local Python test on exact fetched files; no original game resources, no CI or Unity.
owner baseline: DEVICE_FEEDBACK_42058825739_AR.md, CL 520c4cf4, world save/reopen success; WATER-001 remains OPEN, NOT_READY 0/3.
coordination: T3 FX, T4 physical mouse, T5 Resolution/shared APK untouched.

## Result
- Fix commit 34dd118d5aa1615e675e052e9e394f82b82f5125: normalize JSON decoder RecursionError to EvidenceError.
- Regression commits e0403ee12a4a57a0da85978322871d4a87a71ac3 and 8d546062803a77e91c568b704d19c39f390bd96a; 10,000-deep nested array remains under 64 KiB.
- Independent Python JSON decoder reproduction: 10,000 nesting raises RecursionError, 1,500 and 3,000 accepted under local interpreter; robust case uses 10,000. No full checkout test or original shader/Unity/phone run.
- Next: run python -m unittest discover -s tests -p 'test_t2_foam_evidence_gate_20261110.py' at pinned SHA, inspect report producer wiring, resume original Foam pass1 texture identity.
