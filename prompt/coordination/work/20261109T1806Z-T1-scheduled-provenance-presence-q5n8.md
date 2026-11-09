# T1 WATER-001 scope
session_id: 20261109T1806Z-T1-scheduled-provenance-presence-q5n8
origin: scheduled
issue_id: WATER-001
status: active
base_sha: 87ad14f48e6b11ec18232caa577c58e62125dca3
intended_files: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_dispatch_pair_audit.py (if present)
experiment_key: fft-pair-provenance-presence-v1-source-87ad14f
resource_key: none (Python-only, no Unity/CI)
hypothesis: mixed records with missing session_id/build_sha can be accepted as positive pairs when other rows carry provenance; require consistent field presence without rejecting all-legacy records.
taken_over_from: T1 20261109T1705Z-T1-scheduled-session-boundary-p8n4
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; newer 8-Nov CL session remains separate.
T4 owns physical mouse; T5 owns Resolution and packaging. No overlap with those files.
