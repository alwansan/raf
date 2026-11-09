# T1 work scope — 20261109T1213Z-T1-scheduled-dispatch-pass-identity-c8f1
origin: scheduled
baseline_sha: 4edda851a88f533068eee6d4b2d0b8d6cf9d426e
issue: WATER-001 OPEN; owner run 42058825739 entered/saved/reentered world; FFT water remains broken.
experiment_key: T1-FFT-DISPATCH-PASS-IDENTITY-C8F1
files: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_pair_pass_identity_c8f1.py; clients/T1/sessions/20261109T1213Z-T1-scheduled-dispatch-pass-identity-c8f1.md; this work file.
hypothesis: pairing only kernel/resource/FFT size without pass_index/bank/FindKernel/Dispatch identity can conflate distinct FFT passes with identical sequence numbers; check pass-specific identities when recorded on both sides.
shared_resource: none; no Unity/CI requested. T4 owns mouse, T5 Resolution/UI.
validation: synthetic unittest; not runtime/GPU evidence. Check current branch HEAD and path SHAs before write.
taken_over_from: T1 20261109T1110Z sequence canonicalization, B01/B06/B08/B18/B30/B48 evidence.
