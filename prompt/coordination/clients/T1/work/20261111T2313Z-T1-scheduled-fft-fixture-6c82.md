# T1 work — 20261111T2313Z-T1-scheduled-fft-fixture-6c82
origin: scheduled
issue_id: WATER-001
status: active
base_sha: dbf9b24e89dc1d90e3958b026e3aea1d20bf34e2
intended_files: scripts/test_t1_fft_capture_budget.py; prompt/coordination/clients/T1/sessions/20261111T2313Z-T1-scheduled-fft-fixture-6c82.md; prompt/coordination/clients/T1/work/20261111T2313Z-T1-scheduled-fft-fixture-6c82.md
experiment_key: fft-first-divergence-ci-43101033840-fixture-alias-fcb0c5c
resource_key: none (Python-only)
Hypothesis: CI's two positive fixtures reuse one file for reference and observed, conflicting with the new samefile safety guard. Change only fixture inputs to two independent files, preserving the production guard and negative alias tests.
Evidence: https://github.com/alwansan/raf/actions/runs/43101033840/job/130792235243 (two failing tests, exit 2 ValueError).
No Unity/Android build, no T4/T5 files.
