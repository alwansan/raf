# T4 session 20261110T1036Z-T4-scheduled-native-device-gate-b7q2
origin: scheduled
resumed_from_sessions: 20261110T0939Z-T4-scheduled-gate-source-audit-r6m2; 20261110T0841Z-T4-scheduled-ci-proof-k4r8
work_plan_commit: bf3192b48a5cfbe03274fcfbff0f652a71713362
issue: INPUT-005 OPEN; LOCAL-005 OPEN

## Authenticated source findings
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner confirmed world enter/save/exit/reopen on run 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628); package publish failed separately. No regression claim for .rgd.

Read live android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs on feature/android-native-port. Contrary to older assumption that all button/wheel fallback is absent, production currently contains GetMouseButton/GetMouseButtonDown/GetMouseButtonUp/GetMouseScrollDelta and Mouse ScrollWheel wrappers. They first use original Unity Legacy Input and supplement only when requested && nativeCaptured. The native listener records captured button/wheel events, returns false for non-move to preserve original View delivery, and never injects synthetic touch or keyboard events. This is SOURCE evidence only, not a confirmed device fix.

Precise remaining gate: PhysicalMousePresent() checks Unity InputSystem Mouse.all, excludes virtual RaftAndroidTouchLeft, and Update() requires physicalPresent for shouldCapture. If a genuine Android InputDevice mouse is connected but Unity InputSystem has not registered it, requestPointerCapture is never called. Existing physical_mouse_capture_eligibility telemetry can separate this from native denial, but does not itself prove the condition occurred on phone. Native InputDevice enumeration must be capability-filtered and tested before any fallback is merged; a blanket bypass would risk trapping touch users. Source also uses Android View.hasPointerCapture probes and releases on focus/pause, so changing this without evidence risks camera and keyboard regression.

## Limits and next executable step
No fresh CL device trace was read in this cycle; no phone test, signed game build, code behavior change, or CI dispatch. Latest previous T4 source CI 42776921454 succeeded, but is not a device pass. Read a signed-game JSONL containing physical_mouse_capture_eligibility and capture_requested, plus actual Android mouse connection. If inputSystemPhysicalMouse=false while Android InputDevice SOURCE_MOUSE=true and authoredLock/focus permit capture, implement a bounded native InputDevice presence probe, exclude virtual/touch devices, and test keyboard, Escape, release on focus loss, and three buttons/wheel. Coordinate T5 on Resolution separately. Preserve original .rgd and save behavior. No source CI is a claim of real phone input.

status: completed_source_audit; INPUT-005 remains OPEN
