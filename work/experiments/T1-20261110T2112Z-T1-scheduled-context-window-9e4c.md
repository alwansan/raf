# T1 work scope
session_id=20261110T2112Z-T1-scheduled-context-window-9e4c
origin=scheduled
issue_id=WATER-001
status=completed_source_test_pending
base_sha=df3463b79a87c8720a0363e3dd90aa343b14eef3
intended_files=scripts/t1_kernel6_log_context.py; scripts/test_t1_kernel6_context_window.py; clients/T1/sessions/20261110T2112Z-T1-scheduled-context-window-9e4c.md
experiment_key=T1-KERNEL6-TRUE-LINE-WINDOW-20261110-LOG-MARKER-BOUNDARY
resource_key=none (source-only)
hypothesis=The current prior deque counts diagnostic-bearing lines, not physical log lines; distant markers can be misreported as adjacent to kernel-6 failures. Fix line-distance semantics without exposing raw logs.
resumed_from=clients/T1/sessions/20261110T1912Z-T1-scheduled-kernel6-sampling-a6c9.md
Owner 42058825739 Artifact world entry/save/re-entry confirmed; packaging failed. T4 mouse and T5 Resolution/right buttons remain separate scopes. No Unity/CI dispatch.

Outcome: code commits 34ba938, 7875bc0; regression fd02346; checkpoint 6d20466. DNS blocked execution, no CI launched. Follow-up: run unittest, apply scanner to real CL sessions, then original GUID/FindKernel binding.
