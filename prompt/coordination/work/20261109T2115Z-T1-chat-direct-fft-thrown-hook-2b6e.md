# T1 authentic Dx11FFT managed Dispatch synchronous-exception trace scope
session_id: 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
origin: chat
status: active
resumed_from_sessions: 20261109T2030Z-T1-chat-index6-selector-correlation-c2d7; 20261109T2002Z-T1-chat-cl-t105-proof-6e8a; 20261109T2016Z-T1-scheduled-evidence-order-5e91
base_sha: d8da9a55fab4722aca0ff02cb4ea77c9a860265c
issue_id: WATER-001
experiment_key: original-authenticated-dx11fft-2-direct-dispatch-synchronous-throw-safe-trace-v1
resource_key: none; source-only CI, no Unity editor, no Mini or full game native build
intended_files: scripts/t1_stage_original_fft_dispatch_trace.py; tests/test_t1_stage_original_fft_dispatch_trace.py; android-port/Runtime/Platform/T1FftDirectDispatchTrace.cs; android-port/Tests/T1FftDispatchTraceCompile/UnityTraceStubs.cs; docs/T1_ORIGINAL_FFT_SYNC_THROW_TRACE_2026-11-09.md; independent T1 session/work/experiment/event; T5 discussion. No changes to T1 scheduled scripts/t1_shared_fft_device_evidence.py.
hypothesis: existing source-authenticated Android-only BeforeDispatch and AfterDispatch hooks cannot distinguish synchronous Unity ComputeShader.Dispatch exception from missing/rotated AfterDispatch; preserve the *original* call statement and rethrow its original exception, capture only safe kind and call sequence, do not claim async GPU/callback error attribution.
observed: Latest CL/test/shared-20261109-233132-554663211 repeats synthetic R4 T1-05 PASS on source 731d7a68... but no full game Dx11FFT runtime evidence; T5 R5 Mini CI42691609924 SUCCESS, not a new original XAPK.
team_overlap: scheduled T1 latest 2016 evidence-order owns Mini T1 auditor, separate files. T2 Foam and T3 smoke/T4 mouse/T5 labs unaffected; native game build request remains T5-owned.
next_step: implement, run isolated CSharp9 ABI + syntactic source gates + authenticated original private overlay CI, document boundaries.
## Follow-up parser scope (after CI42695722354 SUCCESS)
status: in_progress_trace_parser
additional_intended_files: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_dispatch_pair_native_jsonl.py
hypothesis: original paired JSONL audit currently ignores the newly emitted t1_original_fft_dispatch.threw event, causing an actual synchronous exception to be misclassified as an unexplained missing return. Add fail-closed separate synchronous exception terminal while retaining all earlier paired-record semantics and gpu_execution_proven=false.
ci_plan: existing isolated .github/workflows/raft-t1-fft-dispatch-pair-audit.yml triggers only Python; preserve original hook CI separately, no game APK.
