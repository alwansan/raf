# T1 — 20261108T0712Z-T1-scheduled-fft-ci-syntax-6f2a
origin: scheduled
baseline_sha: a352034d17f3677b9fe70e6962dae3a26d9e71bb
scope_commit: fd623f0a74c88160efea2c4d57ab85b0dc10e096
fix_commits: bda31cd35d7173331835b43cd4e0be1965d84b0c, c229168ef4d25ab88c26dc1045952c444e0cde54, d056bd5f818f75a074b955cdfbe69ea8f77a6a1d
origin: scheduled
issue: WATER-001 OPEN
status: waiting_ci

## Owner priority and evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: source e9c358eda01785b65e4eb14f18723da426635628, artifact install succeeded for enter/save/reenter; publication failed. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57; session 220911-559 23,884 water pass / 3,850 FFT kernel errors; 230108-327 39,132 / 6,026. No new device evidence; kernel index 6 identity still unproven.

## Engineering changes
Previous run 42453584790 failed. Source inspection exposed a double backslash at the end of a Python with-statement in scripts/test_t1_fft_capture_budget.py, which is invalid Python continuation. Fixed to a single backslash. The FFT comparator's manifest preflight still checked a literal backslash-x00 rather than actual NUL, unlike read_private_capture; corrected to actual NUL and added subprocess regression. No private payloads published.

## Validation
Latest CI run 42457872783 queued at 2026-11-08T07:13Z; 42457864030 in_progress, and earlier 42457860036 failed on intermediate commit. Do not claim success until inspect 42457872783. No duplicate dispatch, no Unity build. T4 physical mouse and T5 three buttons/Resolution remain independent.

## Next
Inspect CI failure details on final SHA d056bd5f; fix only proven issue. Continue authentic ComputeShader GUID/FindKernel/Dispatch mapping and paired Vulkan/Unity numeric captures; structure tests are not device evidence. NOT_READY 0/3. Read this session before resuming.
