# T1 WATER-001 — bounded Dispatch audit outcome metrics
session_id: 20261109T1425Z-T1-scheduled-return-metrics-f6a2
origin: scheduled
issue_id: WATER-001
base_sha: b8ccc5f6f787b362e4b246961af5786d140f79ca
status: active
intended_files: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_dispatch_pair_audit.py; prompt/coordination/clients/T1/sessions/20261109T1425Z-T1-scheduled-return-metrics-f6a2.md; this work file
experiment_key: t1-dispatch-return-outcome-metrics-v1-source-b8ccc5f
resource_key: none (CPU-only synthetic trace; no Unity)
hypothesis: returned_count currently includes failure-marked AFTER events, so consumers need separate paired_count and failed_return_count to avoid treating a failed Dispatch return as a successful pair.
owner_evidence: DEVICE_FEEDBACK_42058825739_AR.md, CL immutable 520c4cf; later 2026-11-08 evidence is a separate session.
coordination: no changes to T4 mouse/T5 Resolution; no native build or raw assets.
updated_at: 2026-11-09T14:25:00Z
