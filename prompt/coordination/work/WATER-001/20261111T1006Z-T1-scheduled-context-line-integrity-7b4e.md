# 20261111T1006Z-T1-scheduled-context-line-integrity-7b4e
origin: scheduled
role: T1
baseline_sha: c9547601324338cdd833fbc98f10ebc1eec5ac98
issue: WATER-001 OPEN / NOT_READY 0/3
owner_device: 42058825739; world/save/reopen from artifact confirmed, water/FFT not confirmed.
scope: scripts/t1_fft_pass_proximity.py; scripts/test_t1_fft_pass_proximity.py; unique session file only.
hypothesis: sanitized proximity tool currently accepts context line zero and duplicated line numbers within one context side, allowing malformed provenance and inflated nearest-pass evidence. Restrict context to positive lines, strictly ordered per side, preserve original unknown kernel identity and noncausal interpretation.
experiment_key: T1-FFT-PASS-CONTEXT-INTEGRITY-20261111
shared_resource: none; no Unity build or mini APK.
coordination: T4 pointer capture and T5 right-side panel/resolution remain untouched. T2 Spectrum/Foam files untouched.
taken_over_from: T1 20261111T0905Z pass proximity source, previous source commit 2d55099; owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md.
next: run synthetic tests; obtain original CL scans and authenticated FindKernel/Dispatch evidence; do not infer Unity runtime kernel identity from numeric six.
