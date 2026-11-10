# T2 scheduled session — 20261110T1316Z-T2-scheduled-utf8-gate-p8k2
session_id: 20261110T1316Z-T2-scheduled-utf8-gate-p8k2
origin: scheduled
baseline_sha: c0cf8520c088041c0ccd4b5ececc7c8fc8a38a7f
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739; CL snapshot 520c4cf
resumed_from: clients/T2/sessions/20261110T1224Z-T2-scheduled-json-integer-boundary-m7q3.md
scope: work/experiments/20261110T1316Z-T2-scheduled-utf8-gate-p8k2.md
source_commit: d17862a39f6c37f177c5bd6c4f6b3fe8c63bc684
test_commit: d7154b0db7a3b440737061feab12b9083d56beba
work_update_commit: cc599347b0823f762837d4f9ee0b08c00e24b6f7
result: parse_aggregate_json now wraps malformed UTF-8 UnicodeDecodeError as EvidenceError; three invalid-byte cases added to existing regression test. Initial test fixture accidentally contained literal double-backslash escapes; corrected in test_commit.
verification: source reviewed and commits published. Full unittest NOT RUN; no device/Unity/pixel verification; no CI launched. This is a publication gate hardening, not authentic Foam shader restoration.
next: run python -m unittest -v tests.test_t2_foam_evidence_gate_20261110 on pinned SHA; connect strict gate to evidence producer, then prioritize Mono.Cecil and ZIP2 original Foam/Spectrum/Blur pass/resource/CB mapping.
readiness: WATER-001 OPEN / NOT_READY 0/3; owner world enter/save/reenter remains established, not a water success.
