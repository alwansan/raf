# 20261108T0411Z-T1-scheduled-fft-nul-guard-8d2f
origin: scheduled
issue_id: WATER-001
baseline_sha: 1438f83c9a1eb30521cc8d9079072426ece0b050
resumed_from_session: clients/T1/sessions/20261108T0315Z-T1-scheduled-original-trace-gap-6e91.md
status: active
intended_files: scripts/t1_fft_first_divergence.py; scripts/test_t1_fft_capture_path_nul.py; clients/T1/sessions/20261108T0411Z-T1-scheduled-fft-nul-guard-8d2f.md
experiment_key: fft-private-capture-nul-path-literal-validation-1438f83
resource_key: none (pure Python source, no GPU/Unity)
hypothesis: The capture reader checks the four literal characters backslash-x-0-0 rather than the NUL code point, rejecting a valid POSIX filename while relying on later Path operations to reject NUL.
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Device world save/reentry confirmed, water errors unresolved.
limits: Source-level input validation only; not FFT parity, Unity kernel identity or device evidence. No T4/T5 files or native request.
