# T1 WATER-001 — 20261111T1612Z-T1-scheduled-fft-dedup-7e91
origin: scheduled
baseline_sha: f5891f15c3731e6487adf2f750388a53faca8901
scope: scripts/t1_fft_pass_proximity.py; scripts/test_t1_fft_pass_proximity_duplicate_lines.py
hypothesis: repeated sampled error line in sanitized same-log scan inflates water-pass proximity counts without representing an additional FFT failure.
experiment_key: T1-FFT-LOG-LINE-DEDUP-20261111
shared_resource: none; CPU-only Python unit tests, no Actions dispatch.
owner_device: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 world save/reentry confirmed; water/FFT not confirmed.
coordination: T4 owns physical mouse; T5 owns Resolution and three buttons; no overlap. T2 owns Spectrum/Foam original pass recovery.
expected: reject repeated error-line number even when pass tokens differ; preserve unique-line scans.
status: patch prepared; verification by source-only test pending.
