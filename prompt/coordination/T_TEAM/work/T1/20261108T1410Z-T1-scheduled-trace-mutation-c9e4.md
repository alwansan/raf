# T1 WATER-001 — 20261108T1410Z-T1-scheduled-trace-mutation-c9e4
origin: scheduled
issue_id: WATER-001
base_sha: 0da4625f2f21892c062dbd895e12c6ddeb48690f
status: active
intended_files: scripts/t1_fft_trace_consistency.py; tests/test_t1_fft_trace_mutation.py; prompt/coordination/clients/T1/sessions/20261108T1410Z-T1-scheduled-trace-mutation-c9e4.md; this work file
experiment_key: T1-TRACE-SAME-SIZE-MUTATION-20261108-0da4625f
resource_key: none; Python-only, no Unity/GPU/CI
hypothesis: current bounded reader checks truncation/growth but silently accepts an in-place same-size rewrite while reading, risking a false kernel attribution. Compare descriptor fstat before/after and reject size/mtime_ns/ctime_ns changes.
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Phone world/save/reopen succeeded from run 42058825739 Artifact; water errors persist.
resumed_from_session: 20261108T1312Z-T1-scheduled-trace-shortread-q8m3
limits: does not prove original FFT identity, GPU parity, or phone water rendering.
