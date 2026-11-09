# T1 scheduled checkpoint — simultaneous Dispatch errors
session_id: 20261109T1521Z-T1-scheduled-trace-result-allowlist-b3e8
origin: scheduled
issue_id: WATER-001
resumed_from_sessions: 20261109T1425Z-T1-scheduled-return-metrics-f6a2; 20261108T2022Z-T1-chat-fft-source-gate-d8b4
base_sha: a79704658c2c8fdd061da9014d2711bd14ca83c3

## Owner evidence first
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered/saved/re-entered world from run 42058825739 artifact despite packaging failure. Pinned CL sessions 220911: 23,884 invalid water passes and 3,850 FFT kernel errors; 230108: 39,132/6,026. Separate 8-Nov session 74,359/11,165; not additive. No runtime Unity kernel identity proven. Mouse clicks/Resolution remain T4/T5, do not overwrite.

## Work performed
Scoped plan: prompt/coordination/work/20261109T1521Z-T1-scheduled-trace-result-allowlist-b3e8.md. Source fix e21d1801d53e8cab55da8a15f37390366cbc1ed0; tests 9d75a3c215daf803a0b0e941588886bca11b6762. In scripts/t1_fft_dispatch_pair_audit.py, explicit result=exception with changed kernel used to emit only identity_mismatch due to elif. Now emits both identity_mismatch and dispatch_result_failure; failed_return_sequences also records failure, paired_count stays zero. Added two tests to tests/test_t1_fft_dispatch_pair_audit.py: simultaneous errors, and mismatch with returned success marker.

## Limits
No Python tests executed in this environment (GitHub DNS unavailable for local git); changes inspected through GitHub connector. No Unity, Vulkan, Android GPU, phone, build or new numeric FFT evidence. WATER-001 OPEN / NOT_READY 0/3. Existing source conditional numeric 6 != proven Unity kernel ID.

## Next
Run python -m unittest tests.test_t1_fft_dispatch_pair_audit; inspect actual AndroidRuntimeLog schema before declaring trace applicability. Then authenticate same build/input FFT first divergent pass Vulkan-vs-Unity and verify FindKernel/Dispatch. No duplicate heavy CI.
