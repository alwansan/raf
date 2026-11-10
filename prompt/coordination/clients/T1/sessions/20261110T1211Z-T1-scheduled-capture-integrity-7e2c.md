# T1 scheduled — 20261110T1211Z-T1-scheduled-capture-integrity-7e2c
origin=scheduled
issue=WATER-001
branch=feature/android-native-port

## Owner/device baseline
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner confirmed world entry/save/exit/reentry from run 42058825739 artifact; delivery publication failed. CL 220911-559: 23,884 water-pass and 3,850 FFT kernel errors; 230108-327: 39,132 and 6,026. Never sum distinct sessions. Newer 8 Nov CL: 74,359 water-pass, 11,165 kernel6 errors; no evidence of original FindKernel binding or GPU dispatch. Mouse physical button/scroll remains T4; Resolution and right-hand controls T5; general touch layout deferred.

## Independent work
Existing scripts/t1_fft_readback_provenance.py checks manifest schema, SHA syntax and capture lengths but does not read actual bytes. Added scripts/t1_fft_capture_integrity_gate.py to verify bounded private RGBA32F capture lengths and SHA256 against manifest, reject escape/symlink paths and >128 MiB aggregate, never output pixels. Added tests/test_t1_fft_capture_integrity_gate.py with 4 synthetic controls. Source commits b95c76b41965faf9664dc883eb67d3bf08c22077 and 96f336b028ebf02c106f63031007ba647664ed4e. Work commit ef59ea501b2a2af5696b9674fa9f7464c2c188cf.

Local Python: 4/4 synthetic tests PASS with API-compatible stub for existing validator (network unavailable in container). These are NOT repository-integrated CI tests. No Unity, Vulkan GPU, phone test, native kernel binding, shader restoration, or new APK in this cycle. Existing latest T1 work on Unity computed-only carrier mismatch 63x5 vs buffered 0x5 should be inspected before overlap.

## Next
Run these four tests in repository CI at immutable SHA containing both commits, avoid duplicate Actions; collect private same-build Vulkan/Unity RGBA32F pass readbacks and bind original ComputeShader GUID/kernel names to FindKernel/Dispatch; then run first-divergence comparator. Keep WATER-001 OPEN, NOT_READY 0/3. Do not modify peers' T4/T5 code or shared memory.
