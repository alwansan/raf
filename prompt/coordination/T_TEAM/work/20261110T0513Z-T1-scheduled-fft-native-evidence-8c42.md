# T1 scoped work — 20261110T0513Z-T1-scheduled-fft-native-evidence-8c42
origin=scheduled
issue=WATER-001
baseline_source=feature/android-native-port
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md (run 42058825739; world save/reload success; water FFT errors remain)
files=tests/test_t1_fft_native_trace_contract.py (new, isolated); prompt/coordination/T_TEAM/clients/T1/sessions/20261110T0513Z-T1-scheduled-fft-native-evidence-8c42.md
hypothesis=The passive original FFT trace schema must reject malformed dispatch group counts and must never count a managed Dispatch return as GPU or FindKernel proof.
experiment_key=T1-FFT-NATIVE-TRACE-CONTRACT-20261110
shared_resource=none; no Unity, no APK, no workflow dispatch
non_overlap=New test module only; no edits to T4/T5 files, shader assets, or shared STATUS.
expected_evidence=Source-level unittest, not device FFT verification.
next=Verify tests on a SHA containing them; obtain authentic resource GUID/kernel binding and GPU numeric pass data before changing readiness.
