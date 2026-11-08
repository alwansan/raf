# T1 scheduled session — FFT trace CI coverage
session_id: 20261108T1506Z-T1-scheduled-trace-ci-8f2c
origin: scheduled
baseline_head: d5bfdc4519ebfdfb3c44a64a079e2fc5fd0d50b7
scope: WATER-001 / existing paired FFT diagnostic workflow only
owner_source: docs/DEVICE_FEEDBACK_42058825739_AR.md; apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md
latest_owner_phone: world load/save/reopen confirmed on 42058825739; newer 2026-11-08 CL summary has 74359 invalid water passes, 11165 invalid compute kernels, 7372 cursor warnings. GPU runtime FFT identity remains unproven.
prior_work: T1 trace consistency and file read/mutation guard commits 70cf9dd, a9e58e0, 84580c9, 7d473b3, ed3eb835; earlier paired diagnostic CI success 42457914824 predates newest trace tests.
change: added four pre-existing suites to .github/workflows/raft-t1-fft-paired-diagnostic-checks.yml with path triggers. No new workflow or Unity build.
plan_commit: 48fb80527d74b888135ef45bda169204bcbfe9f5
change_commit: 11b69e69cc31608316949e30e76b32877c130ffd
ci_run: https://github.com/alwansan/raf/actions/runs/42493143730
ci_state_at_checkpoint: queued
status: waiting_ci
limits: no numeric Vulkan vs Unity parity, no actual FindKernel/Dispatch GPU proof, no phone water fix; synthetic tests only.
next: inspect CI 42493143730; if failed, fix first failing assertion. Then use authenticated original compute/kernel mapping and real GPU lab; coordinate T2. Mouse buttons/scroll T4; Resolution T5.
