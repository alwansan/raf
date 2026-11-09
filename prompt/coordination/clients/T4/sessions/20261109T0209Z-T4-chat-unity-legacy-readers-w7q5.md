# T4 chat handoff: native vs Unity Legacy Input reader evidence

session_id: 20261109T0209Z-T4-chat-unity-legacy-readers-w7q5
origin: chat
worker: T4
issue_id: INPUT-005
status: source_integrated_device_pending
resumed_from_sessions:
- 20261109T0157Z-T4-chat-crossframe-click-e4p8
- 20261109T0143Z-T4-scheduled-capture-phase-j6r2
base_sha: f97c9462194dd22c5c09e0f5342cff0a79a0c830
work_reservation_commit: 465becf56ca4fbb068bf1ccc6e7838b876a567fd
experiment_key: T4-Unity2021-Legacy-20-original-mouse-readers-source-routed-counters-nonblocking-v1
resource_key: T4-Unity2021-source-only-android-bridge
scope: Bounded pure source reader observability, no game input return change and no unified Mini or full XAPK build.
intended_files: android-port/Runtime/Platform/PhysicalMouseMotionSource.cs; android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs; android-port/Tests/PhysicalMouse/Program.cs; tests/test_t4_android_pointer_capture_policy.py; own docs, event, experiment, session and work.
source_commits: 67753be5ea18d8dc6af07023b4fb36d4518116f1; b2fdb28e08cd8f210264a704d83fbbdfc101cd16; 201c1b61f7059e1a1553d95ca9105b88004a3004; b376e00a66ba06a593de8cc52398d6cfff7bb85d
ci: https://github.com/alwansan/raf/actions/runs/42549986761
ci_status: COMPLETED_SUCCESS
ci_tests: 66 Python, 152 C#; original SHA+Unity2021 Android+Editor managed compile passed; Unity IL2CPP player NOT built.
report: docs/T4_MOUSE_UNITY_LEGACY_READERS_TELEMETRY_2026-11-09.md

## Restoration and source result
Checked latest T4 scheduled/chat sessions and team Actions, branch HEAD and owner read-only CL/test; no fresh captured=true T4 owner trace. Last T4 source cross-frame mouse capture CI 42548512179 successful; original 20 reader sites already source-staged, but callback telemetry alone could not establish calls to original Unity getters. Chose independent source-only reader instrumentation without touching scheduled analyzer or T5 single Mini.

Implemented pure bounded PhysicalMouseLegacyReaderEvidence with original getter call count and positive Legacy vs fallback counters for three buttons and scalar/vector scroll. Actual patched Unity source wrappers record chosen path only during requested capture; all return values, camera movement, touch, keyboard, settings, local world/.rgd remain intact. Logged first reader, new positive button edge/scroll or 512 further calls and final outstanding log at capture release; counters reset. Explicitly distinguishes getter calls from distinct clicks or gameplay success.

Intermediate CI 42549867596 and 42549924962 failed only due obsolete Python literal checks for previous early-return formatting. Current final CI 42549986761 green (66 Python, 152 C# and pinned original DLL / Unity2021 managed ABI Android+Editor, 20 authentic source sites). No full Unity build or signed APK, and no Android phone acceptance.

## Handoff
Next T4 session read both this file and report, check newest CL/test. When available, compare T4-02 real captured=true callbacks and in a subsequent same-source signed Raft XAPK logs physical_mouse_captured_action_callbacks vs physical_mouse_legacy_reader_evidence. Confirm actual physical LEFT/RIGHT/MIDDLE + wheel V/H and preserve camera, UI, .rgd saving, sound. INPUT-005 OPEN, NOT_READY 0/3. Source-only work does NOT justify rebuilding unified Mini or marking gameplay PASS.
