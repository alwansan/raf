# T3 — shared synthetic GLES frame/readback proof (chat)

- **session_id:** `20261108T1813Z-T3-chat-shared-frame-proof-p6r9`
- **origin:** `chat`
- **worker:** `T3`
- **resumed_from:** `prompt/coordination/clients/T3/MEMORY.md`, `prompt/coordination/clients/T3/state.json`, `apk-for-testing/UNIFIED_IMPLEMENTATION_STATUS.md`, original owner shared lab policy and T_TEAM handoff; historical 2026-11-05 original/export work retained.
- **base_sha:** `73924c998d91eb64be33c883d9922d44981accd4` at work reservation. Earlier observed HEAD `7bb7b0452d56f05dbb39d02d400a39729feaa49b`; T2 wrote a separate work/experiment during this session; no force/reset.
- **issue_id:** RENDER-002 / T3-01..06 shared synthetic color test evidence.
- **scope:** make screenshot evidence conditional on actual GLES frame of matching case, correct per-case readback and no GL error; maintain human visual review.
- **intended_files:** `apk-for-testing/unified/app/src/main/java/com/alwansan/raft/t3lab/T3LabActivity.java`, `tests/test_t3_shared_visual_frame.py`, `docs/T3_SHARED_VISUAL_FRAME_PROOF_2026-11-08.md`, own T3 session/state/MEMORY/work, T3 row only in SHARED_BUILD_READINESS.
- **experiment_key:** `T3-shared-visual-case-frame-handshake-rgba-readback-v1`
- **resource_key:** `T3SharedVisualActivity` (source-only; no GPU build resource reserved).

## Actual work and evidence
1. [204dabb9](https://github.com/alwansan/raf/commit/204dabb9c18b7122550c7aa30a51fdc385de6f45) replaced 1s blind PixelCopy with exact same-case generation handshake and six GLES `glReadPixels` numeric/negative controls; GL errors/timeouts fail closed, do not PASS.
2. [6bb0b165](https://github.com/alwansan/raf/commit/6bb0b165f5849c84b1210eed0c7d8eba00468b2f) enforces case/provenance inside async PixelCopy callback, resets GL program and compiler-negative control across EGL context recreation.
3. [c0a2213b](https://github.com/alwansan/raf/commit/c0a2213bc97d594a3c04c42d956cb51b3c3a291e) added five source-only regression methods. Separate current remote-file invariant scan saw **26/26** source checkpoints, 0 old blind timers and 0 T3 synthetic automatic PASS calls. These are **not** actual phone/Gradle test results.
4. [T3 technical report](../../../..//docs/T3_SHARED_VISUAL_FRAME_PROOF_2026-11-08.md) documents limits. Earlier [unified source compile CI42504045625](https://github.com/alwansan/raf/actions/runs/42504045625) **SUCCESS only for pre-patch source**; not proof this patch compiles.
5. Updated **T3 row only** in `apk-for-testing/SHARED_BUILD_READINESS.md` to **NEED_BUILD** for `shared-20261108-r1`, because native Java driver changes require one new shared APK rather than imported JSON. The T5 integration/signature/queued Actions decision is independent; no full Unity/XAPK request, no other vote changed.

## Limits
Actual T3 synthetic GLES pixels on the POCO device, PixelCopy storage, stable certificate and direct APK remain **UNVERIFIED**. No native mini APK or full game build launched, no CL/ZIP2/authentic shaders/game data modified. T3's synthetic PASS-like readback is only an input to EVIDENCE_READY, never Unity ShaderLab or actual Raft visual acceptance. Owner visual review remains mandatory. RENDER-002/WATER-001 still OPEN, whole game NOT_READY 0/3.

## Next
T5 to run unified Java compile and source-only tests on post-patch SHA, check live Actions/signature/version, integrate single shared Mini if warranted. Then owner checks T3-01..06 images and reports results via one testpack / shared session export. T3 should compare actual pixels and original game errors separately; avoid inferring white materials or fire fixes from synthetic colored quads.
