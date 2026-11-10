# T5 scoped work — 20261110T1850Z-T5-scheduled-pidprefix-9c2e
session_id: 20261110T1850Z-T5-scheduled-pidprefix-9c2e
origin: scheduled
issue_id: PERF-007
base_sha: 19a0b75bb762bbdfb6c80169b39c419dc8c5627b
status: active
intended_files: scripts/t5_cl_pid_epoch_audit.py; tests/test_t5_cl_pid_startup_prefix_real_gate.py; clients/T5/sessions/20261110T1850Z-T5-scheduled-pidprefix-9c2e.md
experiment_key: perf007-startup-unknown-prefix-vs-real-stop-3bc2668-42868458735
resource_key: none (source-only Python)
Hypothesis: unknown process-state samples before first verified PID are observation prefix, not distinct process lifetimes. Explicit stopped state and unknown PID while game_running must still split epochs.
Evidence: https://github.com/alwansan/raf/actions/runs/42868458735 ; 3 failed assertions in source-free startup-prefix gate; other 32 tests pass.
Coordination: T4 owns mouse pointer bridge; no T4 files or Unity CI touched. Preserve source identity and fail closed on real stop/restart.
