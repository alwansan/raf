# 20261107T0710Z-T1-scheduled-schema-5e2a
- origin: scheduled; identity: T1; WATER-001 OPEN / NOT_READY 0/3.
- Owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md, source e9c358eda01785b65e4eb14f18723da426635628; artifact world entry/save/re-entry confirmed, Actions package publishing failed. Log 220911: 23,884 water-pass and 3,850 FFT-kernel errors; 230108: 39,132 and 6,026. Do not equate counts to GPU execution.
- Initial HEAD 456299b789a82888b247dfa2262ad9cc530c44ba; final verified HEAD a3acfd25f5ba77e6cea1321b5b88d3084583cb57.
- Work: prompt/coordination/work/WATER-001/20261107T0710Z-T1-scheduled-schema-5e2a.json (commit 9ae53eb55ac9142c9c9418364717f424ef3f7dca).
- Code commit d2b5a9dfcff0c72823661133694b018d8804c0a4: require exact JSONL trace field set, disallow unexpected raw/private fields; preserve source_sha per-capture checks and cross-backend differences.
- Regression commit a3acfd25f5ba77e6cea1321b5b88d3084583cb57: unexpected-field negative test.
- Test status: NOT EXECUTED. Connector reads/writes successful; container Git cannot resolve github.com (DNS). No CI run dispatched; no native build or device claim. GitHub Actions in_progress count 0 at final check.
- Latest prior T1 session: 20261107T0615Z-T1-scheduled-source-sha-4c8f.md. This change is independent from its mixed source_sha regression.
- Next: execute python3 -m unittest tests.test_t1_fft_trace_first_divergence_7c3a in available CI/runner, then obtain SHA-matched Vulkan/Unity paired captures with real FindKernel, resource bindings and Dispatch; determine earliest numeric mismatch. Keep water OPEN. T4 owns mouse, T5 owns Resolution and three buttons. No touch layout changes.
