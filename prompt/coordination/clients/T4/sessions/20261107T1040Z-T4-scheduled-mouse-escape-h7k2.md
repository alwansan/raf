# T4 scheduled — INPUT-005 Escape/reacquire boundary
- session_id: 20261107T1040Z-T4-scheduled-mouse-escape-h7k2
- origin: scheduled
- base_sha: 3710f1858655fc86aff2c9a450839ca582c747c8
- resumed_from: 20261107T0841Z-T4-scheduled-immutable-mouse-stage-r6p2 and earlier 20261105T1405Z-T4-chat-original-rgd-runtime-k6n8
- work: prompt/coordination/work/INPUT-005/T4-20261107T1040Z-scheduled-mouse-escape-contract.json
- scope: read-only source proof and independent owner-device acceptance contract; no overlap with T5 display/Resolution/button placement or release packaging.

## Verified boundary in current source
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. The owner-confirmed scenario on source e9c358ed / run 42058825739 is world enter, save, exit, reopen; LOCAL-005 remains open for regression. Newer capture is not device-confirmed.

Current android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs explicitly sets originalLockIntent=0 on Input.GetKeyDown(Escape), then Update computes shouldCapture from focus, pause, original lock intent, and physical mouse presence. ApplyCursorLock(Locked) is the only examined rearm of intent. Therefore a return from pause/menu that does NOT invoke an original Cursor.lockState assignment through the adapted call site would leave capture off and use legacy axes. This is a **conditional control-flow risk, not a proven bug**. The source uses a generation-bound OnCapturedPointerListener, requests capture on UI thread, and falls back to legacy Unity axes when native capture isn't confirmed. scripts/t4_adapt_original_mouse_axes.py verifies cardinality 4 X + 4 Y + 2 cursor lock sites and preserves GetAxis/GetAxisRaw and keyboard/button paths.

## Discriminating owner-device smoke
Use a signed package whose source SHA and APK/OBB manifest are recorded. Connect a physical mouse and keyboard, enter existing saved world, move mouse continuously across edges and confirm camera does not stop; check both axes and sensitivity. Press Escape; ensure Android capture releases and Raft menu cursor is usable (not merely black system pointer). Return to gameplay **without disconnecting**: camera must reacquire unlimited relative movement. Repeat via focus loss, mouse unplug/replug and Android app switch, preserving keyboard WASD/Escape and saved .rgd reopen. Correlate ordered markers physical_mouse_capture_requested, physical_mouse_relative, physical_mouse_capture_released, physical_mouse_capture_release_outcome and view_changed/lost with timestamps and gameplay/menu transition; a request marker alone does not establish native capture. Compare UI cursor screenshot with CL pinned 520c4cf... screenshots; never claim CI emulates Android capture.

## Evidence and constraints
- Owner phone feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md and CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- Build candidate source previously established: a1737bd7 (run 42296450023); package release HTTP403, not proof of mouse behavior.
- Latest HEAD checked above; trial vote remains 1/5 needs, no new native dispatch; no game source changes, no raw game assets, no .meta/GUID/.rgd edits.
- Next: trace actual original return-to-game Cursor.lockState call from decompiled authored flow or instrument bounded lock-intent transition; if no rearm is found, implement Android-only safe recapture and validate with existing unit/Unity Editor CI before asking for a device test. Coordinate T5 only for artifact identity and smoke, not its Resolution/buttons scope.
- Result: **source-derived conditional risk isolated, device test pending, INPUT-005 OPEN; LOCAL-005 owner-confirmed limited scenario preserved**.
