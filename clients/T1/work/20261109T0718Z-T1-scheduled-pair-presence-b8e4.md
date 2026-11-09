# T1 WATER-001 scope — 20261109T0718Z-T1-scheduled-pair-presence-b8e4
origin=scheduled
baseline_sha=5c644c14eaae1baeebe4020722b1d1d577fa2ff0
scope=scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_pair_presence_b8e4.py; clients/T1/sessions/20261109T0718Z-T1-scheduled-pair-presence-b8e4.md
hypothesis=BeforeDispatch and AfterDispatch with identical sequence but one-sided identity field can be incorrectly paired, masking a partial trace.
experiment_key=T1-FFT-PAIR-PRESENCE-B8E4
shared_resource=none; no Unity, APK or CI requested.
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md (artifact world save/reload succeeded; water/FFT unresolved).
prior_evidence=20261109T0510Z-T1-scheduled-dispatch-field-pair-6c2e; commit 0ed7c1c; run 42571153053 succeeded for separate runtime gate only.
expected_outcome=reject one-sided identity fields, preserve optional identical fields and no GPU claim.
