# T4 chat — LOCAL-005 JSONL device trace gate

- session_id: 20261105T1408Z-T4-chat-jsonl-evidence-n4r7
- origin: chat
- status: active
- resumed_from_sessions: 20261105T1246Z-T4-chat-load-file-gate-m8q2; 20261105T1338Z-T4-scheduled-v6n9
- baseline_sha: 87c0e1b9b889a67b245891819d44d4d9c0b18898
- started_at: 2026-11-05T14:08:57.818Z
- work_id: prompt/coordination/work/LOCAL-005/T4-20261105T1408Z-T4-chat-jsonl-evidence-n4r7-jsonl-evidence.json
- experiment_key: local005-jsonl-trace-contract-persistentDiagnosticLog-v1-20261105
- resource_key: none
- intended_files: scripts/t4_verify_device_world_save_log.py, tests/test_t4_verify_device_world_save_log.py, .github/workflows/raft-t4-world-save-log-evidence.yml, docs/T4_DEVICE_LOG_EVIDENCE_CHECKER_2026-11-05.md, prompt/coordination/work/LOCAL-005/T4-20261105T1408Z-T4-chat-jsonl-evidence-n4r7-jsonl-evidence.json, prompt/coordination/clients/T4/sessions/20261105T1408Z-T4-chat-jsonl-evidence-n4r7.md

## Evidence and overlap check
T4 other chat active work 20261105T1405Z-chat-original-rgd-runtime-k6n8 owns original 2941B Data.rgd BinaryFormatter/151 managed sibling CLR experiment. This session DOES NOT write its experiment paths or execute its original RGD test. Scheduled T4 1338Z documented phone evidence contract; this session implements a concrete source-free operational JSONL parser to enforce those boundaries. GitHub run sample latest T3 42036281059 succeeded, no queued/in_progress in sampled latest 34; CL main 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29 and last game APK86 remain old. No native run requested.

## Hypothesis
JSONL sequence-based, session-separated *evidence integrity* can be tested now from public PersistentDiagnosticLog source without reading original save data or releasing device logs. It should fail closed for missing candidate binding, incomplete sessions, no user confirmation, missing relaunch and unproven durability. Only aggregate diagnostics are allowed in CI artifact/log.

## Next
Develop and execute targeted tests; capture run and exact assertions; update this file and work, T5 handoff. LOCAL-005 OPEN, NOT_READY 0/3.
