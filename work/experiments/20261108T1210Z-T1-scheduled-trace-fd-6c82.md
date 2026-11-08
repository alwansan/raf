session_id: 20261108T1210Z-T1-scheduled-trace-fd-6c82
origin: scheduled
issue_id: WATER-001
status: active
base_sha: 8111fcc11b5c91fa8eabb3b7892610b143c8d1c7
intended_files:
  - scripts/t1_fft_trace_consistency.py
  - scripts/test_t1_fft_trace_fd_safety.py
  - clients/T1/sessions/20261108T1210Z-T1-scheduled-trace-fd-6c82.md
experiment_key: t1-fft-trace-open-fd-symlink-race-20261108-v1
resource_key: none; Python-only
hypothesis: Current is_symlink/stat/read_text sequence can open a replaced symlink or read a file grown beyond 65536 bytes after stat. Open once with O_NOFOLLOW and bounded descriptor reads.
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner world/save/re-entry confirmed, water errors unresolved.
non_overlap: standalone trace file reader hardening; no Unity, T4/T5 input, or water shader writes.
next: implement bounded fd read and isolated regressions; avoid declaring original kernel mapping or device success.
