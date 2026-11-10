# T2 WATER-001 — 20261110T0520Z-T2-scheduled-call-return-gate-r6p4
origin: scheduled
UTC: 2026-11-10T05:20Z
branch: feature/android-native-port
baseline_HEAD: 71f6fcb4dee95c269d21809b46d8015fc26e62db
work: prompt/coordination/work/WATER-001/20261110T0520Z-T2-scheduled-call-return-gate-r6p4.json

## Evidence and restoration
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first: phone artifact 42058825739 supports world entry/save/exit/reentry, not water rendering; pinned CL 520c4cf4 reports 23,884 invalid water passes and 3,850 FFT kernel errors for 220911, and 39,132 / 6,026 for 230108. Newer owner unified mini-lab policy takes priority over historical independent APKs. Restored latest T2 session 20261110T032515Z-T2-scheduled-cil-join-k8m4 and 20261110T0425Z literal newline repair; older state.json is stale. T3 visuals, T4 physical mouse, T5 Resolution/packaging are separate file scopes.

## Engineering change
Found a genuine fail-open category in scripts/t2_foam_rhs_origin_guard.py: a bare CIL call/callvirt can return void, but was classified CALL_RESULT without a resolved method signature. Changed classify_rhs to require explicit call_returns_value=True for calls, default UNKNOWN. Added source-free regression controls for void, nonvoid, invalid flag and mixed producer. This is a conservative classification guard; a boolean provided by a caller is not itself proof of original signature. Caller must resolve MethodReference.ReturnType from authenticated Mono.Cecil input and prove the exact slice; this tool is NOT wired to Mono.Cecil or runtime texture identity.

Scope commit: 1f13bf6dda8068033fea77cf5db435ed77003922
Source commit: 160c77efc6c41c7181ae2df63e395b3dec8c5ea1
Tests commit: fdc12414e6729360fec8d05ea08a29483412ada6
Test syntax normalization: 4307592c7ff1c3946fe437b20d5f05155010075d

## Limits and next
No test execution yet, no Unity/Android/Adreno proof, no CI requested, no source game shaders or other workers' files touched. Next run targeted Python unittest on pinned SHA, then integrate original method signature extraction into the authenticated Mono.Cecil pipeline. Do not claim Foam pass1 Texture alias or ShaderLab binding; WATER-001 OPEN, NOT_READY 0/3. Review new HEAD/Actions before running CI and avoid duplicate builds.
