# T1 WATER-001 — 20261109T1407Z-T1-scheduled-dispatch-result-4d91
session_id: 20261109T1407Z-T1-scheduled-dispatch-result-4d91
origin: scheduled
scope: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_dispatch_result_4d91.py
hypothesis: a returned event with result=exception currently counts as a successful API-return pair; audit must not pair explicitly failed calls.
experiment_key: T1-FFT-DISPATCH-RESULT-4D91
shared_resource: none (source-only, no Unity/CI)
baseline: last T1 checkpoint 20261109T1213Z-T1-scheduled-dispatch-pass-identity-c8f1
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, CL pinned 520c4cf; 220911-559 23884 water-pass/3850 kernel errors; 230108-327 39132/6026; not additive.
coordination: T4 mouse; T5 Resolution/three controls; no overlap.
acceptance: explicit result=exception must produce dispatch_result_failure and missing return, result=returned remains paired, absent result remains legacy-compatible; no GPU claims.
