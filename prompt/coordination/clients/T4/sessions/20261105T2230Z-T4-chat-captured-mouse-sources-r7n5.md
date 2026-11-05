# T4 chat — captured physical-mouse source and batched motion safety

- session_id: 20261105T2230Z-T4-chat-captured-mouse-sources-r7n5
- origin: chat
- status: active
- base_sha: 376e082f845dd7211a64d976d72f1170d07eb3ab
- resumed_from_sessions: 20261105T2150Z-T4-chat-capture-lease-n5k8; 20261105T2142Z-T4-scheduled-r6w3
- issue_id: INPUT-005
- work: prompt/coordination/work/INPUT-005/T4-20261105T2230Z-T4-chat-captured-mouse-sources-r7n5-event-source.json
- experiment_key: T4-API26-View-captured-SOURCE_MOUSE_RELATIVE-X-Y-vs-TOUCHPAD-AXIS_RELATIVE_X-Y-batched-historical-v1
- resource_key: bounded-source-only-dotnet-Unity2021-originalSHA0a6f0527
- intended_files: prompt/coordination/work/INPUT-005/T4-20261105T2230Z-T4-chat-captured-mouse-sources-r7n5-event-source.json; prompt/coordination/clients/T4/sessions/20261105T2230Z-T4-chat-captured-mouse-sources-r7n5.md; android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs; android-port/Runtime/Platform/PhysicalMouseMotionSource.cs; android-port/Tests/PhysicalMouse/Program.cs; android-port/Tests/PhysicalMouse/PhysicalMouse.csproj; android-port/Tests/PhysicalMouse/UnityBridgeCompile.csproj; tests/test_t4_android_pointer_capture_policy.py; .github/workflows/raft-t4-mouse-capture-bridge.yml; .github/workflows/raft-unity-editor-android-import.yml; scripts/verify_android_offline_candidate.py; prompt/coordination/experiments/T4/20261105T2230Z-T4-chat-captured-mouse-sources-r7n5.json; prompt/coordination/B_TEAM/events/T4/20261105T2230Z-T4-chat-captured-mouse-sources-r7n5.json

## Verified baseline and distinct scope

Last T4 native View capture-loss source integration run 42118499200 **SUCCESS**: 24 Python negative controls; 13 .NET motion tests; authentic ZIP2 original source path verified. No native Android device claim. No T4 source CI currently running, and T1/T2 water/FFT, T3 materials/shader, T5 package/signature reports are in other paths; no full Unity job started by this cycle. Owner's world/save/reopen proof remains bound to 42058825739; system cursor and bars still open.

Android official API26 requestPointerCapture distinguishes SOURCE_MOUSE_RELATIVE where captured MotionEvent.getX/getY are **relative**, and captured SOURCE_TOUCHPAD where getX/getY can be **absolute**, with relative axes AXIS_RELATIVE_X=27/Y=28. MotionEvent historical values are batched, not accumulated, and must be consumed. Existing T4 callback filters only ACTION_MOVE and uses getX/Y unconditionally with no history. That is a source-confirmed parsing gap, not evidence of an observed phone failure.

## Implementation and verified result

Pending.
