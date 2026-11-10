# T2 scope 20261110T1224Z-T2-scheduled-json-integer-boundary-m7q3
origin: scheduled
baseline_sha: 807117e38b8b029b6c8a0a822c0db2aca70094a7
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf; run 42058825739
resumed_from: clients/T2/sessions/20261110T1123Z-T2-scheduled-json-duplicate-q6m4.md
scope: scripts/t2_foam_evidence_gate_20261110.py; tests/test_t2_foam_evidence_gate_20261110.py; this work record and independent session record.
hypothesis: Extremely long JSON integer tokens can trigger Python 3.11 int conversion ValueError before sanitize, breaking the CLI's guaranteed reject-without-traceback contract. Fail-closed behavior must convert parser ValueError to EvidenceError.
experiment_key: T2-FOAM-EVIDENCE-JSON-INTEGER-BOUNDARY-20261110
shared_resources: none; no Unity/GPU/CI/native builds; no T3/T4/T5 files.
readiness: WATER-001 OPEN NOT_READY 0/3. No original ShaderLab or phone claim.
