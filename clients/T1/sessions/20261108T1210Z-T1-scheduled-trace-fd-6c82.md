# T1 scheduled checkpoint — 20261108T1210Z-T1-scheduled-trace-fd-6c82
origin: scheduled
issue_id: WATER-001
resumed_from_sessions: 20261108T1006Z-T1-scheduled-kernel-alias-6f3d; 20261108T0811Z-T1-scheduled-kernel-trace-plan-7e4c
base_sha: 8111fcc11b5c91fa8eabb3b7892610b143c8d1c7
scope_commit: d4091d96c79a7d2f8d469287e03c53f4600240c1
implementation_commit: 84580c9e9928230057f56e5094a177a848f65978
test_commit: 3b0b67751368921bae17c7bf7b1214accb8086ec
origin_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner entered/saved/re-entered world from artifact run 42058825739; water/FFT failures remain.
## Result
- scripts/t1_fft_trace_consistency.py now opens one descriptor with O_NOFOLLOW where supported, checks fstat regular-file/size, reads at most 65537 bytes, decodes UTF-8 strictly, retains duplicate-key rejection.
- scripts/test_t1_fft_trace_fd_safety.py adds five regression cases: regular JSON, symlink, oversized file, duplicate keys, invalid UTF-8.
- This is trace evidence ingestion hardening, not original kernel binding or a water fix.
## Verification and limits
GitHub connector returned commits for both files. Container git ls-remote failed: Could not resolve host github.com. Therefore no local full-repo tests and no claim of CI success. No Unity/Android run launched; no overlap with T4/T5.
## Next
Execute python -m unittest scripts.test_t1_fft_trace_fd_safety and existing trace regressions in CI or a networked checkout. Verify actual original FindKernel/Dispatch/ComputeShader GUID traces and paired Vulkan/Unity pass captures; then identify first numeric mismatch. Do not claim Android GPU parity.
