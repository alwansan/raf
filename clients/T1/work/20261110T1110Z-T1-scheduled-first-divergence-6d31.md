# T1 scope — 20261110T1110Z-T1-scheduled-first-divergence-6d31
origin: scheduled
baseline_sha: 58f770fe2e350169d3d7ecc6fba9512434da11c2
issue: WATER-001
experiment_key: T1-FFT-FIRST-DIVERGENCE-CSV-20261110
files: scripts/t1_fft_first_divergence.py, tests/test_t1_fft_first_divergence.py, clients/T1/sessions/20261110T1110Z-T1-scheduled-first-divergence-6d31.md
hypothesis: a strict same-build same-pass numerical comparator can identify the first divergent FFT pass without claiming original kernel provenance.
shared_resources: none (CPU only); no Unity/CI launch. T4/T5 input/resolution untouched.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; device session 220911-559 23884 water pass/3850 FFT kernel, session 230108-327 39132/6026; do not combine counts. World save/reentry succeeded on artifact 42058825739; publication failed.
proof_boundary: comparator is only useful after real Vulkan and Unity GPU readbacks; synthetic fixture does not establish water recovery.
