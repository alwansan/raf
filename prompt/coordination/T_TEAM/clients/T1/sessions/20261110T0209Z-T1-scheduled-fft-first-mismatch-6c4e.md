# 20261110T0209Z-T1-scheduled-fft-first-mismatch-6c4e
origin: scheduled
issue_id: WATER-001
resumed_from_sessions: 20261110T0112Z-T1-scheduled-device-proof-boundary-c6a2; 20261110T0011Z-T1-scheduled-runtime-gate-recheck-c91e
work: ../../work/20261110T0209Z-T1-scheduled-fft-first-mismatch-6c4e.md
work_commit: 748418f5e4bd6c6d1d95b5ee0fc457d3762ec21a

## Evidence reviewed
- docs/DEVICE_FEEDBACK_42058825739_AR.md and pinned CL snapshot; world save/re-entry success applies to artifact only.
- AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM/PROMPT_AR.md, CHAT_AND_SCHEDULE_AR.md, OPERATING_MODEL_AR.md and unified lab policy.
- scripts/t1_fft_dispatch_pair_audit.py and scripts/t1_shared_fft_device_evidence.py.
- CI jobs: 42723946943 offline PASS, 42723947211 preflight PASS, 42696228231 reconstruct FAIL.

## Finding / experiment boundary
Original FFT passive trace schema hard-codes original_findkernel_callsite_present=false, original_runtime_mapping=unverified, gpu_result=unverified; therefore even valid Before/Returned pairs cannot prove original Unity GPU binding. T1-05 synthetic GLES numeric PASS likewise explicitly records original_raft_compute_executed=false. This is an evidence-boundary finding, not an original water fix. See isolated work record for pass/kernel counts and first-mismatch protocol.

## Remaining
1. Retrieve authenticated original FFT resource GUID and kernel table, and map to Unity FindKernel and actual Dispatch with bound buffers.
2. Capture one-session GPU readback at each pass; compare Vulkan/Unity with same normalization and dimensions; report first mismatch.
3. Correlate original kernel errors with water-pass errors by timestamp and session/build; do not sum different logs.
4. Coordinate with T4 physical mouse and T5 three controls/Resolution; do not edit their files without checking scope.

No new CI, Unity, APK or device execution in this cycle. WATER-001 OPEN/NOT_READY.
