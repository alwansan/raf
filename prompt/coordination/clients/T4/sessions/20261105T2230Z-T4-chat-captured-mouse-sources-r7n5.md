# T4 chat — captured physical-mouse source and batched motion safety

- session_id: 20261105T2230Z-T4-chat-captured-mouse-sources-r7n5
- origin: chat
- status: completed_source_integrated_device_unverified
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

## Verified result — captured mouse source + history

- **Actual source integrated:** `android-port/Runtime/Platform/PhysicalMouseMotionSource.cs` classifies API26 `SOURCE_MOUSE_RELATIVE=131076` vs captured `SOURCE_TOUCHPAD=1048584`, rejects ordinary `SOURCE_MOUSE=8194`, `SOURCE_TOUCHSCREEN=4098` and invalid sources. `AndroidPhysicalMouseCapture.CapturedListener` now consumes relative getX/getY only for mouse-relative events; touchpad movement uses `MotionEvent.AXIS_RELATIVE_X=27/Y=28` instead of absolute touchpad getX/getY. Historical samples (`getHistoricalX/Y` or `getHistoricalAxisValue`) are summed before the latest sample for at most 64 batches; a bigger/invalid packet fails open to Unity. Invalid, zero and excessive motion cannot enable the axis override. Buttons/scroll and ordinary touch return false to original Unity handlers.
- **Real integration:** `android-port/Tests/PhysicalMouse` managed projects include the new class. `.github/workflows/raft-unity-editor-android-import.yml` copies the class into generated Assets/RaftAndroid/Platform together with existing T4 bridge and exact old game-axis adapter. `scripts/verify_android_offline_candidate.py` includes it in managed source checks. Dedicated `raft-t4-mouse-capture-bridge.yml` sparse-checkout includes the file. No edits to game scene, prefab, native build request, T5 UI, touch layout or .rgd.
- **Final bounded CI:** [42121598304](https://github.com/alwansan/raf/actions/runs/42121598304) **COMPLETED SUCCESS**, source SHA `868eac2784efa1fcf7806a23b32bd1a1a1220fcf`, job `127575325748`: original 7 routing +7 exact patch +14 physical capture policy Python tests **28/28**, `.NET` captured motion and source classification **30/30**, compilation against original Unity2021 managed references **SUCCESS**, authenticated private original ZIP2 ILSpy direct axis patch **4 Mouse X, 4 Mouse Y, 2 cursor-lock assignments in five C# files**. The earlier CI on workflow registration [42121540200](https://github.com/alwansan/raf/actions/runs/42121540200) also succeeded. Some *partial intermediate* CI runs failed because the new class had not yet been added to sparse-checkout; no unresolved failure in final SHA.
- **Precise Android source grounding:** for `SOURCE_MOUSE_RELATIVE`, captured `MotionEvent.getX/getY` are relative; for `SOURCE_TOUCHPAD` default captured mode, use axes 27/28 instead of absolute coordinates. Android `MotionEvent` history is not accumulated automatically. References: https://developer.android.com/reference/android/view/MotionEvent, https://developer.android.com/reference/android/view/InputDevice, https://learn.microsoft.com/en-us/dotnet/api/android.views.view.requestpointercapture?view=net-android-37.0.
- **Limitations:** no Unity Editor Android IL2CPP or APK/OBB/XAPK build, no target physical mouse/trackpad on POCO F5 Pro; JNI event-source behavior on device, direction/sensitivity, OS pointer/banner/menu, wheel/buttons, world/save/exit/reopen still unverified. Prior owner-confirmed successful world/save from [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) is a different immutable source SHA. This closes this **source subtask only**; `INPUT-005` remains **OPEN**.

## Next handoff

T5 should deliver next appropriately paired/signed diagnostic APK only when coordinated. Validate exact commit/package/OBB manifest on device, both physical mouse and trackpad if available, captured event source type and camera movement with repeated edge crossings, menu/capture loss/reacquire, keyboard/wheel/buttons/touch, OS system bars and world/save/reopen. If physical input remains blocked, add bounded source-kind counters in diagnostic logs, not raw event coordinates; avoid attributing effects to water/FFT or altering T5 UI. The existing source-only workflow remains available and must not be duplicated without changed inputs.

