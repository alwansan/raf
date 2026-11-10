# T5 session 20261110T1850Z-T5-scheduled-pidprefix-9c2e
origin: scheduled
resumed_from_sessions: clients/T5/sessions/20261110T1554Z-T5-scheduled-fpsjson-k7m2.md and previous PERF-007 scheduled records
base_sha: 19a0b75bb762bbdfb6c80169b39c419dc8c5627b
scope_commit: 1fd6cc649bce624f142edb5cf85141ae9df8bd42
fix_commit: f5a29e49c521b2eb46af486d951b131a8011afd4
issue: PERF-007
origin_evidence: https://github.com/alwansan/raf/actions/runs/42868458735
result: Workflow now actually executes; 18 cohort + 6 PID epoch + 8 integration tests passed, but startup-prefix gate had 3 failures: expected 1 vs 2 epochs (one leading unknown), 1 vs 7 (six leading unknown), 3 vs 4 (unknown then real stop). Root cause: split_verified_pid_epochs treated game_process_state_unknown startup samples as process-stop boundaries. Changed only scripts/t5_cl_pid_epoch_audit.py to keep pre-verification unknown startup samples in the initial epoch, while game_not_running still splits and unknown running PID remains separate.
status: waiting_ci; source change published, no new successful run confirmed yet. No new device FPS or signed APK/OBB attestation. Local test could not run because container DNS blocked; await CI, do not assert PASS.
Files: work/T5-20261110T1850Z-T5-scheduled-pidprefix-9c2e.md, scripts/t5_cl_pid_epoch_audit.py, this session.
Experiment: perf007-startup-unknown-prefix-vs-real-stop-3bc2668-42868458735
Next: check workflow on f5a29e49; inspect both startup gate and pinned real CL gate; if real CL counts differ investigate without loosening provenance. Then return to three right-side buttons, Resolution, and signed APK/OBB identity in non-overlapping T5 scope. T4 retains mouse ownership. No Unity build dispatched.
