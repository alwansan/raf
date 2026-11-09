# T1 scheduled FFT session boundary checkpoint
session_id: 20261109T1705Z-T1-scheduled-session-boundary-p8n4
origin: scheduled
resumed_from_sessions: 20261109T1521Z-T1-scheduled-trace-result-allowlist-b3e8; 20261109T0155Z-T1-chat-direct-dispatch-f7a2
base_sha: 64bb0c80bfbd0edeece98d59115021b6ab74918e
issue_id: WATER-001
work: prompt/coordination/work/20261109T1705Z-T1-scheduled-session-boundary-p8n4.md

## Owner/device evidence first
docs/DEVICE_FEEDBACK_42058825739_AR.md: run 42058825739, original source e9c358eda01785b65e4eb14f18723da426635628; owner entered/saved/reopened world from Artifact, despite failed APK/OBB/XAPK publication. CL 220911: 23884 water pass and 3850 FFT kernel errors; CL 230108: 39132 water pass and 6026 FFT kernel errors. Different sessions must not be summed. Newer 8-Nov feedback also exists. T4 owns mouse physical clicks, T5 owns Resolution/package.

## Engineering
Previously pair auditor checked identity within each sequence but not session/build consistency ACROSS distinct sequences in one JSONL. Added cross_session_provenance errors for session_id and build_sha changes, invalidate all paired results if input mixes provenance. Existing legacy traces with no provenance remain readable but do not attest GPU execution.
source: https://github.com/alwansan/raf/commit/4580a939c981150a75242f29c5a82a7ed7a84f8b
tests: https://github.com/alwansan/raf/commit/e5d267b793f80f1f4fc3cbf39c3ebb1749f10a10
Tests added: cross-session contamination, cross-build contamination, valid two-pair same session; corrected stale duplicate-before assertion to match invalid_sequences behavior.

## Verification limits
Source and test commits published, no Python test execution (container GitHub DNS failure), no new Unity/Vulkan/phone evidence and no CI duplication. This is evidence-integrity work, not FFT numerical correctness, shader import, FindKernel proof, or water fix. WATER-001 OPEN / NOT_READY 0/3.

## Next
Run python -m unittest tests.test_t1_fft_dispatch_pair_audit and review results. Obtain authentic same-build actual Unity FFT Dispatch trace with source-shader GUID and first numeric mismatch. Compare original direct numeric Dispatch separately from named FindKernel probes. Recheck live HEAD and overlapping T1 sessions before changing script.
