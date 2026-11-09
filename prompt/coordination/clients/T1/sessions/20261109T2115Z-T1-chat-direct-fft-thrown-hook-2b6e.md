# T1 — original Dx11FFT synchronous throw semantics and JSONL trace integration
session_id: 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
origin: chat
status: completed_source_ci_verified
resumed_from_sessions: 20261109T2030Z-T1-chat-index6-selector-correlation-c2d7; 20261109T2002Z-T1-chat-cl-t105-proof-6e8a; 20261109T2016Z-T1-scheduled-evidence-order-5e91
base_sha: d8da9a55fab4722aca0ff02cb4ea77c9a860265c
work_id: prompt/coordination/work/20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e.md
issue_id: WATER-001
experiment_key: original-authenticated-dx11fft-2-direct-dispatch-synchronous-throw-safe-trace-v1
resource_key: none, source-only CSharp9 + Python; no Unity editor or Mini game builder
source_commits: d414abd1f30de5362d3ec4324d982a8deaa35be2; f66277c0572065e6fde495a52468542851124281
run_urls: https://github.com/alwansan/raf/actions/runs/42695722354; https://github.com/alwansan/raf/actions/runs/42696197130
latest_owner_CL: https://github.com/alwansan/CL/tree/main/test/shared-20261109-233132-554663211 (synthetic T1-05 still PASS; **not real game trace**)

## Engineering and checks

Existing authentic original `Dx11FFT` has zero direct `FindKernel`, two numeric Dispatch calls, six SetTexture. Existing Android passive wrapper had before/returned only and could not tell synchronous throw from missing/rotated after. The new Android-only `try/catch` logs `threw` with safe fixed kind, then bare `throw;` preserving actual exception; Unity Editor unchanged original statements. Helper never logs exception details or private assets. Parser reports separate thrown sequences and contradictions, never GPU proof.

Changes: `scripts/t1_stage_original_fft_dispatch_trace.py`, `tests/test_t1_stage_original_fft_dispatch_trace.py`, `android-port/Runtime/Platform/T1FftDirectDispatchTrace.cs`, `android-port/Tests/T1FftDispatchTraceCompile/UnityTraceStubs.cs`; `scripts/t1_fft_dispatch_pair_audit.py`, `tests/test_t1_fft_dispatch_pair_audit.py`, `tests/test_t1_fft_dispatch_pair_native_jsonl.py`. Independent doc/experiment/event/work/discussion. T1 scheduled Mini source `scripts/t1_shared_fft_device_evidence.py` untouched.

[CI42695722354](https://github.com/alwansan/raf/actions/runs/42695722354) SUCCESS, 17/17 Python + actual .NET10 C#9 ABI run + SHA original DLL / ILSpy private source decompile and original2 Dispatch preservation. [CI42696197130](https://github.com/alwansan/raf/actions/runs/42696197130) SUCCESS, 45/45 native/legacy JSONL parser tests. Earlier red CI42695525795 due preprocessor fence and comment test, both corrected and preserved as negative evidence.

Limits: No original Unity/game/device call executed, no actual event from this *new* hook yet. Source-only CI cannot establish water fix or numeric original GPU parity. WATER-001 OPEN/NOT_READY 0/3.

Next: use this exact hook in an authorized full-game build on a matching SHA and inspect actual raw `raft-logs` sequence; do not request new Mini test or pretend that current installed full game contains this new hook.
