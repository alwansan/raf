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
