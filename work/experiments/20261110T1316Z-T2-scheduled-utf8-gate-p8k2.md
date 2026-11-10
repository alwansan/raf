# T2 scoped experiment — 20261110T1316Z-T2-scheduled-utf8-gate-p8k2
origin: scheduled
baseline_sha: c0cf8520c088041c0ccd4b5ececc7c8fc8a38a7f
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; run 42058825739; CL 520c4cf
hypothesis: parse_aggregate_json() raises bare UnicodeDecodeError on invalid UTF-8, breaking the documented EvidenceError API for untrusted aggregate evidence bytes.
files: scripts/t2_foam_evidence_gate_20261110.py; tests/test_t2_foam_evidence_gate_20261110.py; own session and this work file only.
experiment_key: T2-EVIDENCE-UTF8-FAILCLOSED-20261110
shared_resource: none; no Unity/CI/GPU/build
scope: strict input boundary; no changes to shaders or T3/T4/T5 files. Preserve NOT_READY.
verification_plan: unittest direct API invalid UTF-8 bytes and valid aggregate; no device inference.
status: source_fixed; tests committed but not executed
source_commit: d17862a39f6c37f177c5bd6c4f6b3fe8c63bc684
test_commit: d7154b0db7a3b440737061feab12b9083d56beba
result: UnicodeDecodeError is normalized to EvidenceError in parse_aggregate_json; test covers malformed byte, overlong encoding and UTF-8 surrogate sequences.
verification: source and tests published; unittest NOT RUN in this cycle; no Unity or device validation.
next: python -m unittest -v tests.test_t2_foam_evidence_gate_20261110 at pinned SHA; connect sanitizer to producer, then resume authentic Foam/Spectrum/Blur mapping.

