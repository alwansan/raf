# T1 scheduled checkpoint — 20261109T1407Z-T1-scheduled-dispatch-result-4d91
session_id: 20261109T1407Z-T1-scheduled-dispatch-result-4d91
origin: scheduled
UTC: 2026-11-09T14:07Z
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md (42058825739 Artifact world enter/save/reenter succeeds; packaging failed). CL pinned 520c4cf; 220911-559: 23884 water passes/3850 FFT kernels; 230108-327: 39132/6026. These are separate sessions, not additive.
prior: clients/T1/sessions/20261109T1213Z-T1-scheduled-dispatch-pass-identity-c8f1.md
work: clients/T1/work/20261109T1407Z-T1-scheduled-dispatch-result-4d91.md
plan_commit: a7a900c06cb3ff74cfbbed5fdca395a3c8006c83
code_commit: dcaee69667fb7c84cef9d9687e74bff7547d5e6a
test_commit: 4a71dce1d517a0b7cc0bba8c6248720325aa3f7a
result: FFT pair audit now rejects AFTER records explicitly carrying result other than returned; avoids treating an exception as a normal Dispatch API return. Legacy no-result records remain parseable. Four regression tests added.
verification: source and tests committed; execution still pending (local git DNS unavailable). No CI/Unity/APK triggered. No GPU proof or numeric Vulkan/Unity parity established.
coordination: no modifications to T4 mouse or T5 controls/Resolution. Touch layout remains deferred.
next: run python -m unittest discover -s tests -p 'test_t1_fft_dispatch_result_4d91.py' and existing pair tests; inspect actual Android JSONL result values; bind original FFT resource GUID and FindKernel/Dispatch, then first numerical Vulkan/Unity mismatch. WATER-001 OPEN/NOT_READY.
