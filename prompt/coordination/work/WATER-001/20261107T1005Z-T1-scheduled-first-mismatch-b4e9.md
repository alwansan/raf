# 20261107T1005Z-T1-scheduled-first-mismatch-b4e9
origin: scheduled
issue_id: WATER-001
status: completed_source_test_added_not_executed
baseline_sha: 958ab2c600ab122904c0a19c447c1184643a426b
intended_files: scripts/t1_fft_trace_first_divergence_7c3a.py; scripts/test_t1_fft_first_mismatch_order_b4e9.py; prompt/coordination/clients/T1/sessions/20261107T1005Z-T1-scheduled-first-mismatch-b4e9.md
experiment_key: fft-trace-first-mismatch-order-schema-v1-96f8e148
resource_key: none (local Python; no GPU/Unity)
hypothesis: comparator scans all coordinate differences before numeric differences, so it may report a later coordinate mismatch instead of the earliest numeric mismatch.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739
scope: isolated comparator regression, not Unity runtime or physical mouse/Resolution owned by T4/T5.
updated_at: 2026-11-07T10:05:00Z

result_commit: 0e94ac912c8c972dd8b78dbcb93fb58075c7b8ca
session_commit: a651b74fb729e213a13552aa725a18f5c4880952
finding: mixed mismatch ordering already implemented; added regression coverage only.
validation: not executed (container DNS prevents checkout); no Unity/GPU/device claim.
next: execute unittest against repository source and obtain original matched Vulkan/Unity capture.
