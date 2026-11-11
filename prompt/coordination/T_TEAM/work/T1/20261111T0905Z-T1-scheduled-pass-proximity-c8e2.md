# T1 work — 20261111T0905Z-T1-scheduled-pass-proximity-c8e2
origin=scheduled
baseline_sha=9b5a5bbd0e96bc460536e74a1c8ec3b9f64bd10c
issue=WATER-001
scope=New independent sanitized pass-proximity analyzer, not T2 shader source or T4 mouse or T5 display/build.
hypothesis=Existing scanner captures pass markers adjacent to kernel-6 errors but the cross-session comparison does not distinguish same-line, preceding, and following water pass markers. A bounded independent tool can summarize those relationships without claiming causality.
experiment_key=T1-FFT-PASS-PROXIMITY-20261111
shared_resource=none; no Unity/CI dispatch.
inputs=scripts/t1_kernel6_log_context.py JSON output with --errors-only; owner report docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57 read-only.
planned_files=scripts/t1_fft_pass_proximity.py, scripts/test_t1_fft_pass_proximity.py, clients/T1/sessions/20261111T0905Z-T1-scheduled-pass-proximity-c8e2.md.
acceptance=Pure Python synthetic tests, no raw log content, no kernel identity assertion, no cross-session timeline inference.
