# T5 checkpoint 20261108T0850Z-T5-scheduled-artifact-expiry-b6f2
origin: scheduled
session_id: 20261108T0850Z-T5-scheduled-artifact-expiry-b6f2
resumed_from_sessions:
- clients/T5/sessions/20261108T0750Z-T5-scheduled-artifact-provenance-a83c.md
- clients/T5/sessions/20261108T0650Z-T5-scheduled-ci-provenance-91ac.md
base_sha: 7989e3c05abb8a522fc02062c0377ade0cde6fa7
scope_commit: 86010427081ffad6f52b4d15f554939c9d1cf162
latest_head_at_checkpoint: 86010427081ffad6f52b4d15f554939c9d1cf162
work: work/T5/20261108T0850Z-T5-scheduled-artifact-expiry-b6f2.md
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md

## Independent live verification 2026-11-08 08:50 UTC
- Rescue run: https://github.com/alwansan/raf/actions/runs/42110297871
- artifact ID 13454900880, name t5-retained-native-delivery-42058825739, size 5948243834 bytes, digest sha256:41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef; expired=false; expires_at=2026-11-08T21:12:40Z.
- This is GitHub archive integrity metadata, **not** APK/OBB inner-file hashes, versionCode, or proof of phone installation.
- Original device-confirmed run 42058825739 uses e9c358eda01785b65e4eb14f18723da426635628; world enter/save/exit/reentry owner-confirmed for that artifact only.
- Trial round trial-20261106-r1: T4 'needs'; T1/T2/T3/T5 'does not need'. No consensus and no new native request.
- Recent unrelated T4 classifier run https://github.com/alwansan/raf/actions/runs/42463928346 failed at 'Verify source-only classifier regression suite'. T4 owns this code; do not edit its files or claim root cause from step status alone.
- Latest T5 source-only LogRaft regression success remains https://github.com/alwansan/raf/actions/runs/42452502335 on aa2d6c3, not the current HEAD.

## Blocker and next
- This tool session has read-only artifact metadata, not an authenticated binary download/private durable storage destination. No transfer performed, so archive survival after expiry is unproven.
- **Urgent**: authenticated owner-controlled download/stream copy of artifact 13454900880 to authorized private durable storage before 2026-11-08T21:12:40Z; verify GitHub archive digest and separately inspect signed APK manifest, versionCode, OBB main/patch names, inner SHA256/size. Avoid public raw asset release.
- Later compare device-installed package identity and original CL LogRaft session provenance; SurfaceFlinger presented FPS is not Unity FPS.
- UI three right-side buttons and Resolution remain open; no UI/source edits in this limited provenance checkpoint.
- No Unity build, release, CL writes, T4 mouse modifications or readiness claims. NOT_READY 0/3.
