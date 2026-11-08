# T1 WATER-001 independent scope
session_id: 20261108T2212Z-T1-scheduled-tolerance-preflight-7b4e
origin: scheduled
baseline_sha: a4f521d416f5f503b197642b2adbf213d7371f88
issue_id: WATER-001
hypothesis: invalid NaN/Inf/negative FFT comparison thresholds should fail before reading private GPU capture bytes.
experiment_key: t1-fft-tolerance-preflight-20261108
resource_key: none; source-only, no Unity or shared CI dispatch
intended_files: scripts/t1_fft_first_divergence.py; tests/test_t1_fft_tolerance_preflight.py; this work and session record
taken_over_from: clients/T1/sessions/20261108T2106Z-T1-scheduled-firstpass-name-preflight-5c21.md
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; world/save/reentry succeeded from artifact 42058825739, package publishing failed, water/kernel faults remain.
source_commit: dcf9bc3c28173b005b4b1bd4253a7a887b702621
test_commit: 93d5d104ddec81b13b17625164ef4948a786da8c
ci_observed: 42523525581 success on 9ac294ff; does not cover this test.
status: source_fixed_test_pending
limits: diagnostic safety only; no proof of original kernel resource, FindKernel, Dispatch, numeric FFT parity or phone water.
next: run python -m unittest tests.test_t1_fft_tolerance_preflight; coordinate first real original Unity kernel binding trace and same-input Vulkan/Unity first-pass capture.