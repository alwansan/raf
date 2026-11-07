# T4 scheduled — mouse lock intent telemetry

- session_id: 20261107T1240Z-T4-scheduled-mouse-lock-trace-k5p9
- origin: scheduled
- baseline_sha: adfc52f314188a2f955028dd197b803a44f6d549
- scope_commit: b43de692d4b24040c76a3a71aa16ed6afc213d14
- implementation_commit: 27fc3baf94b06ecff8410ecb5ce9e27d67a162d9
- scope: prompt/coordination/work/INPUT-005/20261107T1240Z-T4-scheduled-mouse-lock-trace-k5p9.json
- previous: prompt/coordination/clients/T4/sessions/20261107T1138Z-T4-scheduled-capture-rearm-v4n8.md
- origin source: docs/DEVICE_FEEDBACK_42058825739_AR.md (owner device success, not a new mouse acceptance)

## Change and test discriminator

Added Android-only, transition-only `physical_mouse_lock_intent` telemetry in `AndroidPhysicalMouseCapture.ApplyCursorLock` and Escape handling. Events: `authored_lock`, `authored_unlock`, `escape_release`. Does not modify Cursor.lockState semantics, Mouse X/Y, keyboard, touch, buttons, Unity Editor stub, .meta, GUID, .rgd or resources. No per-frame logs or raw input data. Instrumentation is exception-shielded. Re-read source and used the current blob SHA for the update; no forced push.

Compare these new events with `physical_mouse_capture_requested`, `physical_mouse_relative`, `physical_mouse_capture_released` and `physical_mouse_capture_release_outcome` on the next signed APK. If return from pause has no `authored_lock`, inspect authored menu resume lock assignment; if `authored_lock` appears but no request, inspect PhysicalMousePresent/focus; if request appears but no relative samples, inspect native View capture and source delivery. `authored_lock` alone never proves successful capture.

## Evidence and limits

Owner reports world entry/save/exit/reopen on 42058825739, source e9c358ed; LOCAL-005 stays open. Pinned CL screenshots and logs in the owner report show cursor/menu anomalies and water/FFT errors; do not infer current Android mouse success from those older files. Latest queried branch SHA at start adfc52f314188a2f955028dd197b803a44f6d549; recent Actions 42365737052 and 42365731144 completed success on earlier SHAs. No new Unity build dispatched and no device test. This is source-level instrumentation, not a functional capture fix. T5 owns three-button placement, Resolution and package delivery. No shared CI resource used.

## Next

Run targeted source/Unity Editor compile validation of this small Android-only change when available, then capture the Escape->menu->resume trace on a signed APK with manifest provenance; preserve keyboard and world .rgd regression test. If instrumentation shows a missing authored rearm, patch only that transition with evidence, not unconditional recapture. INPUT-005 remains OPEN; NOT_READY 0/3.
