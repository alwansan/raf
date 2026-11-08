# T1 WATER-001 scheduled checkpoint
session_id: 20261108T2310Z-T1-scheduled-runtime-evidence-gate-k7p2
origin: scheduled
base_head: 5179bb7e5dfb180a032d2c7aea9e85ed4e5d0a6a
owner_device_reference: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner successfully entered/saved/reopened world from run 42058825739 artifact, despite package publishing failure.
current_evidence: CL 20261108 raw Spectrum 16:49:17.552 and summary water 16:49:17.579; 11,165 kernel-index6 messages from full summary; no authenticated mapping from numeric 6 to Unity runtime kernel. Original Dx11FFT C# Dispatch arg 6 is conditional on size256 bank0, not FindKernel proof. See CI42519853981 success and prompt/STATUS.md.
latest_checked_head: 5179bb7e5dfb180a032d2c7aea9e85ed4e5d0a6a
actions: 42529039014 completed success (source dcf9bc3; not coverage of later 93d5d10 tests); 42523525581 success; 42519487402 shared mini APK success; no pending in latest 12 runs.
scope: prompt/coordination/work/WATER-001/20261108T2310Z-T1-scheduled-runtime-evidence-gate-k7p2.md
implementation: scripts/t1_fft_runtime_evidence_gate.py commit 0913539ba87af9c8ad16502f73feeebbb66c5698; scripts/test_t1_fft_runtime_evidence_gate.py commit daa0c16911d1d095a94b72c9b3b6394e5a9c4e73.
purpose: reject runtime FFT evidence without immutable build SHA, session, shader GUID, named kernel, matching FindKernel and Dispatch IDs, groups, FFT size/bank/pass and binding names. Prevent false inference from original numeric 6. Does not reconstruct original shader or run Unity.
validation: tests authored but not yet executed; do not claim CI/device success. No Unity build or new Actions launched.
next: run python3 -m unittest scripts.test_t1_fft_runtime_evidence_gate; capture sanitized runtime evidence from same installed build; then compare first differing FFT pass against pinned Vulkan reference. Coordinate with T2 and T5, no changes to T4/T5 mouse/resolution.
status: SOURCE_ONLY / WATER-001 OPEN / NOT_READY 0/3.
