# T1 scope — 20261111T0811Z-T1-scheduled-fft-device-triage-a91e
origin: scheduled
baseline_sha: c6158c26db367ab1dc44ab5c82634fd60eac16fd
issue: WATER-001
experiment_key: T1-DEVICE-42058825739-FFT-TRIAGE-20261111
resource: none; read-only analysis, no Unity/CI/GPU reservation
files: clients/T1/work/20261111T0811Z-T1-scheduled-fft-device-triage-a91e.md; clients/T1/sessions/20261111T0811Z-T1-scheduled-fft-device-triage-a91e.md
hypothesis: the two CL sessions show persistent FFT kernel/pass failures, but raw counts alone cannot establish regression or a specific original ComputeShader identity.
evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57; scripts/t1_compare_kernel6_sessions.py.
observations: first session 23884 water-pass and 3850 FFT kernel errors; second 39132 and 6026. Ratios second/first 1.638 and 1.565 respectively. Within-session FFT-to-water ratios 0.1612 and 0.1540. Different log durations and gameplay phases are not controlled. No per-frame or GPU comparison is valid.
next: obtain sanitized per-session scan outputs with hashes, first event context, timestamps and scene phases; then correlate with original compute resource GUID/kernel table and instrument FindKernel/Dispatch. Do not infer index 6 is a stable kernel name across binaries.
status: evidence_gap; no CI launched, no runtime claims.
