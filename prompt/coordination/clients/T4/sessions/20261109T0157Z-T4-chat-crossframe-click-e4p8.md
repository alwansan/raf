# T4 chat session — Android cross-frame primary button dedup

- **session_id:** `20261109T0157Z-T4-chat-crossframe-click-e4p8`
- **origin:** chat; **worker:** T4; **issue:** INPUT-005 OPEN
- **resumed_from_sessions:** `20261109T0144Z-T4-chat-downup-correlation-n6q2` (chat); `20261109T0143Z-T4-scheduled-capture-phase-j6r2` (scheduled); `20261108T1958Z-T4-chat-legacy-button-wheel-bridge-y8m2` (chat).
- **base_sha:** `80d128223fbe79bb27305bba9efdf2304ffd1df5`; independent work reservation commit `1bff8a1ed1d428c2a7a08d9bf695f42e6665301d`.
- **experiment_key:** `T4-real-CL-13-same-eventtime-click-crossframe-native-dedup-Unity2021-source-v1`
- **resource_key:** `T4-PhysicalMouseButtonWheelFrame-runtime-source-only-authenticated-Unity2021`
- **scope/intended_files:** `PhysicalMouseMotionSource.cs`, `AndroidPhysicalMouseCapture.cs`, `android-port/Tests/PhysicalMouse/Program.cs`, `tests/test_t4_android_pointer_capture_policy.py`, T4-only `docs`, experiment, event, work and session. No shared T5 Mini/pack/full-game build request/other worker file modified.

## Live recovery and ownership
Reviewed RESTORE_AR / CHAT_AND_SCHEDULE_AR / portrait shared-lab owner instructions, latest T4 scheduled capture-phase session (separate analyzer scope), current T5/T1/T2/T3 work, GitHub Actions, latest CL/test (no new captured T4 trace), original authenticated button/wheel source staging. No concurrent T4 Unity heavy build or overlapping source owner found. Publishing source in one atomic CAS commit preserved teammates' HEAD; no force/reset/cancel.

## Problem from actual CL and source
Old genuine owner `CL@4680f5dc` has 13 `ACTION_DOWN/UP actionButton=0` matching 13 explicit left `ACTION_BUTTON_PRESS/RELEASE` with identical eventTime/source/capture. This only proves uncaptured Android View callbacks. Existing C# bit masks coalesced events in the same frame, but a Unity frame boundary between paired Android callbacks could replay an extra edge. The new guard uses positive Android `eventTime`, source and physical `deviceId` with capture epoch Reset. Missing IDs preserve events. Right/middle, wheel, camera and touch unchanged.

## Engineering commits and CI
- **Source atomic commit `b5f9e60d991ff3d6d998e2f2b91e2e7ea1a30fcf`:** four files; capture callback now supplies real eventTime/deviceId; dual order and same eventTime edges suppressed across Unity frames; C# regressions for time/source/device/reset.
- **First CI [42548460164](https://github.com/alwansan/raf/actions/runs/42548460164) FAILED** at Python policy due undefined MOTION variable; skipped C#/Unity. Explicit diagnostic, not player runtime failure.
- **Policy correction `435665c85b32f67eb745ce9a0c25e0384dd4e8bd`** defines source reading for policy.
- **Final https://github.com/alwansan/raf/actions/runs/42548512179 COMPLETED SUCCESS:** six Python suites totaling 66 tests, 139 C# checks; pinned original compiled DLL SHA check, Unity2021 Android and Editor managed bridge compilation, private exact 20 source locations staged, no raw source artifact and no Unity player build.
- Report: `docs/T4_ANDROID_MOUSE_CROSSFRAME_EDGE_DEDUP_2026-11-09.md`; experiment `prompt/coordination/experiments/T4/20261109T0157Z-T4-chat-crossframe-click-e4p8.json`; event `prompt/coordination/B_TEAM/events/T4/20261109T0157Z-T4-chat-crossframe-click-e4p8.json`.

## Handoff, limitations, and next step
**State:** T4 source-bound mouse duplicate hazard guarded and source CI tested, **not phone-verified**. `INPUT-005 OPEN`, full game `NOT_READY 0/3`; no new Mini/Unity XAPK and T4 shared-lab vote NO_BUILD unchanged. Current CL/test lacks real captured=true with three buttons and V/H scroll; request ON alone never establishes OS capture.
**Next:** T4-02 on current unified Arabic Portrait mini: owner presses Capture ON in blue INPUT PAD and physically tests LEFT/RIGHT/MIDDLE + V/H scroll, exports CL/test; correlate capture true against deviceId/eventTime. When authorized signed Raft build includes T4 source, test legacy Unity consumers, camera and keyboard/touch and world/.rgd save/reopen. Future T4 scheduled cycle should read THIS independent session and CI before modifying overlapping runtime files. Never claim device pass from source evidence.
