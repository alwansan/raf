# T5 scheduled — UI allocation checkpoint
session_id: 20261111T0647Z-T5-scheduled-ui-gc-r8p3
origin: scheduled
resumed_from_session: 20261111T0548Z-T5-scheduled-rightbuttons-r6k2
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57
base_sha: d9f2b6a325d31d58d2e2136997a2dc6afa1fac7b
scope_commit: c6fe293b81b16b564240493816a2c5939837a225
source_commit: 5e7a1faa0b13323a269b0e7c8d794b563acf389d
test_commit: d823329ba192f66fd66d80e413779a522fbedb91

## Work
AndroidTouchUiPanel.FitRightButtonsToSafeArea was allocating two temporary arrays and performing three Transform.Find operations every enabled frame (up to 120Hz on target). Cache the three right-side RectTransforms during Create and keep fixed offsets in a static readonly array; preserve all existing anchors, order, scaling, gamepad and Settings. Updated source regression to reject repeated searches in Update/FitRightButtonsToSafeArea and assert offsets. No T4 mouse file touched.

## Verification
Re-fetched live source and test at HEAD d823329ba192f66fd66d80e413779a522fbedb91. Static checks confirm exactly three cached Find calls in Create and zero in the per-frame fit path. Mathematical fit checks PASS for safe heights 720,360,224,180,120. This is source-only verification; Python test CI, Unity compile, Android device and FPS impact not yet confirmed. No Unity build launched. T4 mouse classifier Actions 42974039265 succeeded at 2026-11-11T06:40Z on earlier SHA 22c1b3f, not evidence of this change.

## Remaining
Run tests/test_t5_right_diagnostic_safe_area.py via cheap CI when available and check Unity compile. Investigate Resolution Settings bindings, signed APK89/OBB actual SHA and signer, LogRaft per-epoch device FPS comparison. No claim of new phone measurement or readiness. Owner world save/re-entry remains limited to artifact 42058825739. NOT_READY 0/3.
