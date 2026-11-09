# T1 bounded Adreno GLSL FFT-like butterfly Mini CASE scope
session_id: 20261109T1915Z-T1-chat-mini-butterfly-a9f3
origin: chat
status: active
base_sha: 90547ec2d38d9e1255ceb89da313f7151064c0a9
issue_id: WATER-001
experiment_key: t1-shared-mini-ssbo-butterfly-two-pass-local512-source-only-android15-adreno730-v1
resource_key: shared-mini-testpack:coordination-T5 (no build request; T5 owns one unified APK)
resumed_from_sessions: 20261109T185616Z-T1-chat-fft-audit-run-34c243; 20261109T1806Z-T1-scheduled-provenance-presence-q5n8
intended_files: apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1ComputeProbe.java; apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/MainActivity.java (T1 auto regex only); apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java (T1 routing regex only; T5 shared owner); apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/ArabicLabStrings.java (T1 case entry only); apk-for-testing/unified/pack/team-testpack.json (T1-05 only; T5 merged pack owner); scripts/validate_unified_testpack.py (T1 routing); tests/test_unified_testpack.py (T1 count); tests/test_t1_mini_fft_butterfly_source.py (new only); .github/workflows/raft-t1-mini-butterfly-source.yml (new); session/work/event/discussion files.
hypothesis: Existing T1-01..04 confirm GLES3.2 capability and 16-word simple SSBO dispatch only; a 512-invocation two-program complex butterfly with one shared SSBO and barrier, CPU independently checked, could distinguish a real Adreno 730 large-group/complex arithmetic/readback failure from purely source naming/Unity registration issues. It is strictly a synthetic Android workload, NOT the real Raft kernel, not original shader pixels, and cannot solve original FindKernel identity.
current_owner_CL: 20261108-232759-468049775 / v0.2.13 T1-01..04 four fresh PASS; device compute 1024 invocations theoretical, no original Unity proof.
team: latest T2 Foam, T3 smoke, T4 mouse, T5 OBB/pack. Their driver files untouched. Shared host T5 to receive scoped notice and review. T1 will not trigger unified Mini request or build XAPK itself.
next_step: implement bounded compiled-in-only T1-05 GLSL numerical butterfly + Java reference and negative contract tests; source-only CI; T1 only vote NEED_BUILD on success and handoff T5 single Mini build/release. No user action until a verified new APK actually exists.
