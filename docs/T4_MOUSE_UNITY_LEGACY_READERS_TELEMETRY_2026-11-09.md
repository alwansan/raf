# T4 — Unity Legacy Input source reader telemetry (2026-11-09)

**Worker:** T4; **origin:** chat; **session_id:** 20261109T0209Z-T4-chat-unity-legacy-readers-w7q5; **issue:** INPUT-005 OPEN.

## Evidence gap
The real physical mouse camera motion was reported working under Android Pointer Capture, but game LEFT/RIGHT/MIDDLE and wheel still lacked gameplay proof. The pinned original ZIP2 Assembly-CSharp source has **20 Legacy Input button/scroll reader sites in 12 files** (4 Down, 6 Held, 2 Up, 6 scroll axis, 2 mouseScrollDelta). Prior source CI staged a native physical-mouse fallback at these sites, but the Android View callback counters could not demonstrate whether an original Unity reader was invoked. The latest read-only owner CL/test uploads still lack the manual T4-02 captured=true trace; the older 13 LEFT and 55 VSCROLL records are from uncaptured Mini.

## Implemented source diagnostic
- `PhysicalMouseLegacyReaderEvidence` in `android-port/Runtime/Platform/PhysicalMouseMotionSource.cs`: bounded 11 source slots (Held/Down/Up x Mouse0/1/2, scalar scroll axis, vector scrollDelta), per-slot getter calls, positive original Unity values, positive physical captured fallbacks. Thread-safe, no disk, no Unity API, no fake input.
- `android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs` now records the *actual original getter call results* only while capture requested, using the unchanged native-first return semantics. Camera Mouse X/Y and touch untouched.
- Rate-limited `physical_mouse_legacy_reader_evidence` and `_final` log with epoch, requested, captured, total getter calls, positive native and fallback values, and per-slot counters. First observed reader, new positive edge/wheel, or 512 more polls; outstanding values at release then reset. Log explicitly sets `countersAreGetterCallsNotClicks=true; unityGameplayVerified=false`. No per-frame logging or app/gameplay claim.
- `android-port/Tests/PhysicalMouse/Program.cs`: source-only actual getter ledger tests. `tests/test_t4_android_pointer_capture_policy.py`: verifies wiring to real wrapper methods, preservation of original input first and no event injection.

## Reproducible source results
Commits: collector `67753be5ea18d8dc6af07023b4fb36d4518116f1`; tests `b2fdb28e08cd8f210264a704d83fbbdfc101cd16`; Android bridge `201c1b61f7059e1a1553d95ca9105b88004a3004`; static policy final `b376e00a66ba06a593de8cc52398d6cfff7bb85d`.

**CI 42549986761 SUCCESS:** 66 Python (7+15+9+22+5+8), 152 C# assertions; original private managed DLL SHA authenticated, Unity2021 Android+Editor managed ABI compilation successful, original exact mouse source staging passed. Earlier CI 42549867596 and 42549924962 failed on stale static policy text, then tests updated; no game runtime failure established. CI 42549842731 was marked canceled, not by T4.

See https://github.com/alwansan/raf/actions/runs/42549986761 .

## Limits and next action
No Unity full player build, signed APK or fresh Android gameplay test. Getter calls are not unique physical clicks and even a positive value is not proof that the authored game action completed. **INPUT-005 OPEN; NOT_READY 0/3**. No change to shared Mini/Testpack/owner CL/other worker files, keyboard, touch, audio, Settings or save .rgd. Next authorized same-SHA game build should correlate `physical_mouse_captured_action_callbacks` and `physical_mouse_legacy_reader_evidence` after true Pointer Capture + physical LEFT/RIGHT/MIDDLE and V/H wheel, and verify actual gameplay and world/save regressions. The unified Mini T4-02 test needs capture_request=ON and real captured=true observations separately.
