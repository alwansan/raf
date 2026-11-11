# T5 isolated scope — 20261111T1348Z-T5-scheduled-ledger-identity-q7m2
origin: scheduled
base_sha: a7a5f894fcbbd7cfdcbb08cee3a716ce48a6ec6f
issue_id: INTEGRATION-001
intended_files: prompt/coordination/B_TEAM/events/T1/20261109T2002Z-T1-chat-cl-t105-proof-6e8a.json (identity metadata only); independent T5 session and work files
experiment_key: t5-t2-summary-missing-event-id-43028966025-source-6485e86
resource_key: none; no Unity or CI dispatch
hypothesis: canonical summary fails on missing event identity, not git race. Run 43028966025 stack trace confirms ValueError Missing record identity on this exact T1 record. Add explicit event_id matching existing session_id without changing proof/status/owner; no modification of T2 workflow or shared script. Verify next run before claiming fix; other malformed events may remain.
status: active
coordination: T1 retains ownership of synthetic GLES evidence; metadata-only compatibility fix, T2 retains workflow; no change to test semantics.
