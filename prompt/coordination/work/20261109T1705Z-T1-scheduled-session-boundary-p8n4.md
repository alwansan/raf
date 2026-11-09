# T1 work scope — 20261109T1705Z-T1-scheduled-session-boundary-p8n4
session_id: 20261109T1705Z-T1-scheduled-session-boundary-p8n4
origin: scheduled
issue_id: WATER-001
status: active
base_sha: 64bb0c80bfbd0edeece98d59115021b6ab74918e
resumed_from_sessions: 20261109T1521Z-T1-scheduled-trace-result-allowlist-b3e8; 20261109T0155Z-T1-chat-direct-dispatch-f7a2
experiment_key: t1-fft-jsonl-cross-sequence-session-contamination-v1
resource_key: none (source-only lightweight audit)
intended_files: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_dispatch_pair_audit.py; prompt/coordination/clients/T1/sessions/20261109T1705Z-T1-scheduled-session-boundary-p8n4.md; this work file
hypothesis: Even when each Before/After pair agrees, a merged JSONL containing different session_id/build_sha across sequences can be reported as successful. Prevent this evidence contamination without claiming GPU proof.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 source e9c358eda01785b65e4eb14f18723da426635628, CL 220911 23884/3850, CL 230108 39132/6026; world save/reopen confirmed, package publish failed.
coordination: T4 mouse, T5 resolution/packaging; no Unity/CI dispatch or touching shared files.
