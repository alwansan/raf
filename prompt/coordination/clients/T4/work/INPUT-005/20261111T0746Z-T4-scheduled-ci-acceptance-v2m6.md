# T4 INPUT-005 CI acceptance — 2026-11-11 07:46 UTC
session_id=20261111T0746Z-T4-scheduled-ci-acceptance-v2m6
origin=scheduled
baseline_head=69915d51e045d43eb6287f52184c0e2470e2f80c
scope=Independent verification of prior T4 mouse tests and device-evidence gap; no shared source edit.
files=prompt/coordination/clients/T4/work/INPUT-005/20261111T0746Z-T4-scheduled-ci-acceptance-v2m6.md
experiment=INPUT-005-T4-CI-42974039265
resource=none; no Unity/APK/OBB build
taken_over_from=prompt/coordination/clients/T4/sessions/20261111T0640Z-T4-scheduled-ci-wire-q8m3.md
## Evidence
- Owner phone 42058825739 (source e9c358e) confirms world creation/save/exit/reopen, not mouse buttons. LOCAL-005 remains open; do not touch .rgd.
- Owner 8 Nov confirms captured camera movement but LEFT/RIGHT/MIDDLE and wheel fail in game.
- Actions 42974039265 on 22c1b3f5fc57a0b64508c5527f2e2f87a3250916 completed success (verified GitHub API 11 Nov 2026); this resolves prior waiting_ci for the source-only T4 mouse trace classifier workflow.
- Existing AndroidPhysicalMouseCapture.cs callback records button/scroll actions and returns false for nonmove; Unity legacy readers fall back to captured frame only if requested and nativeCaptured. This code inspection is not Android acceptance.
- Latest observed branch HEAD 69915d51e045d43eb6287f52184c0e2470e2f80c. No duplicate CI requested.
## Next
Inspect same-build real captured action and legacy-reader logs from CL; classify callback absent vs frame reader absent. Coordinate with T5 shared mini lab, no separate APK. Preserve keyboard, Settings, audio, touch, .rgd and T5 Resolution ownership. INPUT-005 remains OPEN.
status=ci_source_pass_device_unverified
