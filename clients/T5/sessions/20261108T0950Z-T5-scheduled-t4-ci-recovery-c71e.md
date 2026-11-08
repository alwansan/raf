# T5 checkpoint — 20261108T0950Z-T5-scheduled-t4-ci-recovery-c71e
origin: scheduled
session_id: 20261108T0950Z-T5-scheduled-t4-ci-recovery-c71e
resumed_from_sessions:
- clients/T5/sessions/20261108T0850Z-T5-scheduled-artifact-expiry-b6f2.md
base_sha: d672b9865951733767f544126d7467fae5b4fcf7
scope_commit: f86788369ca69dd2f2465dc235e0e3d03a87a671
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md

## New verified evidence (2026-11-08 09:50 UTC)
- Previous T4 mouse classifier CI 42463928346 on 2bcb9bc78bbc4c9be1424d91b02cd709e3cf4b88: completed/failure, 2026-11-08 08:40 UTC.
- Later T4 mouse classifier CI **42468530415** on 08a3f0a92cfce05ff1f30e592e7ad8f29252898c: completed/**success**, 2026-11-08 09:45 UTC. Commit message: `T4: align retry telemetry regression with first-request/else-if branches`. This supersedes the previous *source-only regression failure* but does NOT prove physical mouse capture on Android.
- Current branch HEAD at first inspection d672b9865951733767f544126d7467fae5b4fcf7; no T4 file modified by T5.
- Trial round trial-20261106-r1 remains T4 needs, T1/T2/T3/T5 do not need, hence no 5/5; owner-direct run 42281310905 is a separate failed Unity run and not permission to repeat.
- Rescue artifact 13454900880 last independently verified by prior T5 checkpoint at 08:50 UTC: expires 2026-11-08T21:12:40Z; **not revalidated in this cycle**. Archive SHA256 is not the installed APK or OBB hash. No durable copy performed.
- Owner-confirmed world entry/save/exit/reentry applies only to run 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628).

## Scope result and limits
- Verified resolution of the prior T4 *CI regression failure* by a later successful run; no duplication of T4 fixes or Unity dispatch.
- Cannot infer physical mouse Android behavior, three right-side buttons, Resolution, package identity, or device FPS from this CI.
- No APK/OBB downloaded or installed; no new phone measurement. Source-only checks do not establish GPU correctness.
- Status NOT_READY, no 3/3 readiness claim.

## Next
1. Preserve artifact 13454900880 in authorized private durable storage before expiry, then inspect signed APK versionCode, OBB filename/size/SHA and installed phone provenance. Do not publicly publish raw game assets.
2. Inspect T5-owned three-button safe-area and Resolution implementation, with isolated file scope and no T4 physical mouse overlap; validate using source tests and later device test.
3. Link LogRaft valid SurfaceFlinger estimates to specific game phase and package; do not label presented FPS as Unity FPS.
