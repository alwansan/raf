# T1 scheduled session 20261109T0212Z-T1-scheduled-fft-radix2-8d31
origin=scheduled
scope=WATER-001 / FFT runtime evidence validator
owner_device_reference=42058825739 (world entry/save/reentry confirmed; water not confirmed)
baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57
hypothesis: a zero or non-power-of-two FFT length was being accepted as complete binding evidence, obscuring the first divergence.
files: scripts/t1_fft_runtime_evidence_gate.py; scripts/test_t1_fft_runtime_evidence_gate.py
experiment_key: T1-FFT-RADIX2-PREFLIGHT-20261109
shared_resource: none; source-only
result: FFT runtime evidence rejects fft_size=0, 1, and non-powers-of-two. Added 3 regression cases for 0, 300, and 2.
commits: e705184aaedc8b81792527f4a3004c9b5002a785; 2fcdeef50b23481ca07e68660dcd4fbc8958fa85
validation: code inspection only; new tests not executed in this session. No Unity runtime/phone evidence and no build or CI dispatched.
caveat: radix-2 assumption applies to authentic FFT stages; if non-radix-2 FFT discovered, revise contract based on source evidence.
next: execute python -m unittest scripts.test_t1_fft_runtime_evidence_gate; then collect actual ComputeShader GUID/FindKernel/Dispatch and per-pass numeric captures from the same build. Preserve T4 mouse and T5 resolution scope.
status: SOURCE_FIXED / TEST_PENDING; WATER-001 OPEN / NOT_READY
