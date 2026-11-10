# T2 scheduled checkpoint — 20261110T2122Z-T2-scheduled-utf8-fixture-v8n2
session_id: 20261110T2122Z-T2-scheduled-utf8-fixture-v8n2
origin: scheduled
base_sha: 9bbfe70693218cbdcf213eb26a26a188fcaaaa52
resumed_from_session: 20261110T1923Z-T2-scheduled-evidence-cli-ci-q8v4
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner entered, saved and reentered world from run 42058825739 artifact; water errors remain.
work: prompt/coordination/work/experiments/20261110T2122Z-T2-scheduled-utf8-fixture-v8n2.md
issue_id: WATER-001
finding: test_invalid_utf8_is_rejected used ASCII bytes b"\\\\xff" and therefore tested JSON parse failure rather than UnicodeDecodeError. Corrected invalid UTF-8 case to bytes([0xff]); retained ASCII malformed JSON as separate regression.
verification: source-only change; workflow .github/workflows/raft-t2-foam-evidence-cli-gate.yml watches this test file and will run on push. CI outcome pending; no Unity/device validation.
limitations: evidence sanitizer and CLI are not proven integrated with actual publisher; no original Spectrum/Foam/Blur shader or RenderTexture/CB0 binding restored by this change.
next: inspect triggered CI on this commit; trace report producer/upload step and enforce sanitizer there; continue original Foam RenderTexture producer/consumer and CB0/ShaderLab evidence with T3.
readiness: WATER-001 OPEN; NOT_READY 0/3.
