# T4 — 20261107T0335Z-T4-scheduled-artifact-retention-v8q2
origin: scheduled
session_id: 20261107T0335Z-T4-scheduled-artifact-retention-v8q2
base_sha: a8af80674302b9418c753916c9d8afe8b6f5a4a2
scope_commit: 75e6560835c5af1bcd42da6bfe8f9fba410f7d3f
resumed_from_sessions:
- 20261107T0245Z-T4-scheduled-release-permissions-p4x8
- 20261107T0135Z-T4-scheduled-release403-a6q9

## New live evidence (2026-11-07 03:35 UTC)
- Owner phone test [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source e9c358eda01785b65e4eb14f18723da426635628: **actual world entry, save, exit and re-entry succeeded**, per docs/DEVICE_FEEDBACK_42058825739_AR.md. Do not regress .rgd, FileManager, keyboard, audio or Settings; no new phone evidence for mouse.
- [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) source a1737bd736e276d53df808442cfae3b1eea0d488: reconstruction succeeded, publication failed HTTP403. GitHub artifact endpoint NOW confirms signed checkpoint ID 13550196498 (2,974,171,581 bytes), expired=false, expires 2026-11-09T23:48:15Z; delivery ID 13549514149 (5,948,365,703 bytes), expired=false, expires 2026-11-09T23:49:06Z. These are **two distinct recoverable artifacts**, not a published release or verified device install.
- Current branch HEAD before reservation a8af80674302b9418c753916c9d8afe8b6f5a4a2, after scope commit 75e6560835c5af1bcd42da6bfe8f9fba410f7d3f; no in_progress runs returned for branch query at this check. No duplicate native request.
- Existing T5 trial vote remains 1/5 'needs'; prior direct owner request is separate. No assumption that a newer HEAD patch is inside immutable a1737bd7 build.

## Engineering decision and handoff
Artifact expiration is a **time-bound recovery risk** independent of whether HTTP403 gets resolved. T5/delivery owner should recover the already signed output before 2026-11-09 23:48 UTC and preserve provenance, SHA256, manifest, versionCode, OBB naming and APK signature; prefer existing signed checkpoint over rebuilding. Confirm file-level hashes from downloaded content rather than relying only on GitHub artifact ID or archive size. No credential values in logs. GitHub GET release permission does not establish release POST authorization.
T4 owns physical mouse acceptance: Android View pointer capture and relative motion in gameplay, Raft cursor in menu, left/middle/right buttons, focus loss, mouse disconnect, fullscreen system bars, keyboard unchanged. Test on **matching signed APK+OBB** from immutable build source, not current HEAD. Keep LOCAL-005 OPEN; prior save success is specific to old device artifact and must be rechecked as regression test on new candidate.

## Result / limits / next
This run verified artifact retention/expiry and documented a concrete recovery deadline. No production code change, Unity run, release retry or device test. Scope is completed as read-only artifact retention verification. Next: T5 archive signed outputs before expiry and diagnose effective release token rights; T4 use recovered package for device mouse/save regression or independently inspect source-only capture logic if no device feedback. NOT_READY 0/3; INPUT-005 open.
