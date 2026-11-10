# T1 scheduled session 20261110T0606Z-T1-scheduled-native-provenance-3e7b
origin=scheduled
status=completed_source_only
baseline_sha=9c96a135a27d249cb1a4927727ea392c1f21c98f
scope_commit=957ae32c1cfc7cc8f90a5c4f5ef2fe5453b2d654
source_commit=d858cdecd7186c48b0fd22ac01bf6c872357cf88

## Evidence and result
Read owner phone feedback docs/DEVICE_FEEDBACK_42058825739_AR.md first. World entry/save/re-entry succeeded from artifact; FFT water errors remain open. Device logs 220911-559: 23,884 water pass errors and 3,850 FFT kernel errors; 230108-327: 39,132 and 6,026 respectively; do not aggregate across sessions or imply causation. Current newer owner 8 November lab guidance requires unified mini APK and separates synthetic from authentic FFT.

Read current team requirements and audited scripts/t1_fft_dispatch_pair_audit.py. Added two source-level regression cases to tests/test_t1_fft_native_trace_contract.py: reject mismatched build_sha between native before/return and reject dropped build_sha provenance on return. Both expect paired_count=0 and explicit provenance errors; these assertions test existing implementation, not Unity execution. Tests are committed but NOT executed in this session; CI success 42747722414 predates the new tests and cannot validate them.

GitHub HEAD at initial inspection 9c96a135a27d249cb1a4927727ea392c1f21c98f. Recent Actions 42763994149, 42763994110, 42763993805, 42763993875 successful, but none proves original FFT. No CI dispatch, no shared resources, no T4/T5 edits, no release claim. Scope recorded independently in work/experiments/20261110T0606Z-T1-scheduled-native-provenance-3e7b-scope.md. No source assets exposed.

## Next
Run python -m unittest tests.test_t1_fft_native_trace_contract on commit containing d858cde, then extract authentic FFT GUID/resource and FindKernel/Dispatch runtime evidence from one build/session. Compare Vulkan/Unity numeric output from first differing pass only after actual GPU capture. WATER-001 OPEN NOT_READY 0/3. Preserve T4 physical mouse and T5 resolution/three-button ownership; no general touch layout redesign.
