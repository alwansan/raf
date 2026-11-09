# T1 scheduled checkpoint
session_id: 20261109T1213Z-T1-scheduled-dispatch-pass-identity-c8f1
origin: scheduled
UTC: 2026-11-09T12:13Z
baseline_sha: 4edda851a88f533068eee6d4b2d0b8d6cf9d426e
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md — Artifact 42058825739 world enter/save/reenter succeeded, packaging failed; 220911-559 23884 water-pass / 3850 FFT-kernel errors; 230108-327 39132 / 6026; sessions not additive. Newer 8-Nov evidence 74359 / 11165 from separate session.
work: work/experiments/20261109T1213Z-T1-scheduled-dispatch-pass-identity-c8f1.md
code_commit: a524af308c40542cb3dffd9e4f64c4e0c4e409a5
test_commit: d2c4ac7b1cc1371210edcbd1e3a17676cdc99a5f
change: identity pairing now also checks pass_index, bank, fft_size, kernel_index, find_kernel_result, dispatch_kernel whenever present. Prevents false match for different FFT passes or kernel indexes with identical sequence. Five synthetic regressions added.
verification: code and tests published, test execution pending; local git access fails DNS. No Unity build, APK or CI triggered. No GPU or device evidence inferred.
shared scope: T4 physical mouse; T5 Resolution and three buttons; untouched.
next: execute python -m unittest tests.test_t1_fft_pair_pass_identity_c8f1 and existing pair suite; compare actual Android JSONL field names; collect paired Unity FindKernel/Dispatch and Vulkan-vs-Unity first divergent numeric pass. WATER-001 OPEN, NOT_READY.
