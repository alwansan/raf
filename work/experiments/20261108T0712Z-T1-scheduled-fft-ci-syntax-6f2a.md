# T1 scope 20261108T0712Z-T1-scheduled-fft-ci-syntax-6f2a
origin: scheduled
baseline_sha: a352034d17f3677b9fe70e6962dae3a26d9e71bb
issue: WATER-001 OPEN
hypothesis: FFT CI failures stem from a malformed double backslash line continuation in scripts/test_t1_fft_capture_budget.py; manifest preflight also checks literal \\x00 rather than actual NUL.
files: scripts/test_t1_fft_capture_budget.py; scripts/t1_fft_first_divergence.py; scripts/test_t1_fft_capture_path_nul.py (read-only unless needed); clients/T1/sessions/20261108T0712Z-T1-scheduled-fft-ci-syntax-6f2a.md; this scope file.
experiment_key: t1-fft-ci-syntax-nul-20261108; shared_resource: none; no Unity/native build.
owner baseline: 42058825739 artifact world enter/save/reenter confirmed; water pass/kernel errors remain, no authentic FFT kernel mapping confirmed.
previous: 20261108T0609Z-T1-scheduled-m8q2; run 42453584790 failed. T4 physical mouse and T5 buttons/Resolution are independent scopes.
status: IN_PROGRESS

## 07:14Z evidence update
Final earlier CI 42457872783 failed with 7 subprocess cases, all due to ModuleNotFoundError: No module named 'scripts' when running comparator by absolute script path. Other 9 tests passed, including NUL path and Dispatch coverage. Job log ID 128660656875. Fixed subprocess invocation to python -m scripts.t1_fft_first_divergence in commit a29329608e1ec4e5378f222ce427a25e8a5fe742. Waiting for new CI at this SHA; no duplicate dispatch. This is an import/CI fix, not FFT numeric parity or water device confirmation.

## Verified CI result
Run https://github.com/alwansan/raf/actions/runs/42457914824 completed SUCCESS on immutable code SHA a29329608e1ec4e5378f222ce427a25e8a5fe742. Source-only regression verified; WATER-001 remains OPEN; next original kernel/FFT GPU evidence. Scope completed, not device-confirmed.
