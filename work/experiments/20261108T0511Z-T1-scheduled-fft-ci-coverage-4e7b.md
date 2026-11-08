# T1 WATER-001 — FFT regression CI coverage
session_id: 20261108T0511Z-T1-scheduled-fft-ci-coverage-4e7b
origin: scheduled
status: active
base_sha: 2ed6b7d00ea11cb00f4ea8104b0cdfc12590362b
issue_id: WATER-001
intended_files: .github/workflows/raft-t1-fft-paired-diagnostic-checks.yml; work/experiments/20261108T0511Z-T1-scheduled-fft-ci-coverage-4e7b.md; clients/T1/sessions/20261108T0511Z-T1-scheduled-fft-ci-coverage-4e7b.md
experiment_key: t1-fft-ci-existing-synthetic-plus-budget-nul-dispatch-tests@2ed6b7d
resource_key: none (source-only Python CI)
taken_over_from: clients/T1/sessions/20261108T0411Z-T1-scheduled-fft-nul-guard-8d2f.md

## Evidence and hypothesis
Owner phone run 42058825739 confirmed world save/reentry but water errors 23884/3850 and 39132/6026 in two CL sessions. Run 42445720118 succeeded on 9a85ea92, but workflow does not invoke scripts/test_t1_fft_capture_budget.py, scripts/test_t1_fft_capture_path_nul.py or scripts/test_t1_fft_dispatch_coverage.py; previous session explicitly marked them unexecuted. Extend existing T1 source-only workflow to run these tests on a new commit; no duplicate native build, no claims of GPU parity.
