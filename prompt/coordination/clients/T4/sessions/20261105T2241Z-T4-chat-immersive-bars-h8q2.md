# T4 chat — Android system-bar immersive guard

- session_id: 20261105T2241Z-T4-chat-immersive-bars-h8q2
- origin: chat
- status: completed_source_integrated_device_unverified
- issue_id: INPUT-005
- base_sha: 04e0e891d6c333638a4e8f43e09edef47057bd31
- resumed_from_sessions: 20261105T2235Z-T4-scheduled-u8k3; 20261105T2230Z-T4-chat-captured-mouse-sources-r7n5
- work: prompt/coordination/work/INPUT-005/T4-20261105T2241Z-T4-chat-immersive-bars-h8q2-system-bars.json
- experiment_key: T4-Android26-29-legacy-flags-Android30plus-WindowInsetsController-SystemBars-Unity2021-originalABI-source-guard-v1
- resource_key: bounded-T4-source-only-Unity2021-managed-ABI-original-dll-0a6f0527
- intended_files: prompt/coordination/work/INPUT-005/T4-20261105T2241Z-T4-chat-immersive-bars-h8q2-system-bars.json; prompt/coordination/clients/T4/sessions/20261105T2241Z-T4-chat-immersive-bars-h8q2.md; android-port/Runtime/Platform/AndroidImmersiveSystemBars.cs; android-port/Runtime/Platform/AndroidSystemBarPolicy.cs; android-port/Tests/PhysicalMouse/PhysicalMouse.csproj; android-port/Tests/PhysicalMouse/UnityBridgeCompile.csproj; android-port/Tests/PhysicalMouse/Program.cs; tests/test_t4_android_immersive_system_bars.py; .github/workflows/raft-t4-mouse-capture-bridge.yml; .github/workflows/raft-unity-editor-android-import.yml; scripts/verify_android_offline_candidate.py; prompt/coordination/experiments/T4/20261105T2241Z-T4-chat-immersive-bars-h8q2.json; prompt/coordination/B_TEAM/events/T4/20261105T2241Z-T4-chat-immersive-bars-h8q2.json

## Proven baseline and no-overlap

T4 chat built physical mouse captured relative source/trackpad handler and succeeded source ABI CI42121598304. T4 scheduled fixed stale posted pointer release at 75bc6bda, guarded by 42ca7eb, [CI42122830565](https://github.com/alwansan/raf/actions/runs/42122830565) SUCCESS. Different scope: no View pointer-capture file or other client code will be edited here. T5 Resolution changes stay untouched. Owner physical feedback artifact42058825739 proved world/save/reopen only for original source e9c358; system bar annoyance still open and no newer phone proof.

Android reference: https://developer.android.com/develop/ui/views/layout/immersive — games can hide bars using WindowInsetsController and transient swipe behavior. Android 15 system gestures remain a mandatory user affordance. Plan API30+ platform WindowInsetsController (no androidx dependency), API26-29 additive legacy system UI flags, only focused foreground Unity window, no change to Screen/resolution or input capture.

Live HEAD 04e0e891d6c333638a4e8f43e09edef47057bd31. 0 noncompleted recent Actions in selected page. No native build or duplicate T4 job started by this scope.

## Implementation and evidence

## Verified Android system bars source implementation and controls

- Implemented `android-port/Runtime/Platform/AndroidImmersiveSystemBars.cs` at [40b567a2](https://github.com/alwansan/raf/commit/40b567a2f2772a2489359848d9cd2a79ab78b7b4), with Unity Android-only `BeforeSceneLoad` singleton. It requests full-screen immersive bars on the Activity UI thread only while active/focused/unpaused, with limited 15-second policy reapplication, no Unity input/cursor/Resolution changes. API30+ obtains native `WindowInsetsController`, `WindowInsets.Type.systemBars()`, sets behavior `BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE=2`, and calls `hide()`. This preserves Android mandatory Back/Home swipes; cannot guarantee that transient bars never appear. API26-29 merges `FULLSCREEN/HIDE_NAVIGATION/IMMERSIVE_STICKY/LAYOUT*` into existing decor flags, never clears Unity bits.
- Pure `AndroidSystemBarPolicy.cs` plus `android-port/Tests/ImmersiveBars/` executable C# controls establish SDK-version branch, additive/idempotent high-bit preservation and foreground/focus/pause gating. New `tests/test_t4_android_immersive_system_bars.py` guards native Android-only lifecycle, modern/legacy methods, UI-thread operations, system OS exits and native pipeline. Both classes are staged by `.github/workflows/raft-unity-editor-android-import.yml` and `scripts/verify_android_offline_candidate.py`, and the new test workflow `.github/workflows/raft-t4-immersive-system-bars.yml` has bounded independent concurrency and no Unity Editor/native build.
- [CI42124859112](https://github.com/alwansan/raf/actions/runs/42124859112) **COMPLETED SUCCESS**, job `127586307830`, source `4a4e986fa3df4490f69e02c239a2cbde6d8f877f`: **7/7** source policy Python tests, **18/18** C# executable policy controls, exact ZIP2 Assembly-CSharp.dll original size/SHA verified and native component compiled against original Unity2021 CoreModule/AndroidJNIModule. Initial [CI42124747838](https://github.com/alwansan/raf/actions/runs/42124747838) FAILED due test-only high-bit literal CS0266 (`uint` assigned to `int`); fixed to `unchecked((int)0x80000008u)` in the next commit. This failure did not involve Android runtime code.
- **Not claimed:** no full Unity Editor Android IL2CPP build, no signed APK+OBB or device test. The system may always briefly display transient bars for deliberate OS gestures. Confirm Android 15 behavior, system cursor, true physical-mouse rotation, T5 original Settings/resolution and original world/save/reopen on a future exact signed candidate. Existing owner phone proof is bounded to 42058825739, source e9c358eda0; unrelated to the new immersive fix.
- No modification to T5 UI/Resolution, T4 original mouse capture, touch, input buttons, audio, world serialization, .meta/GUID or build-request JSON. No running Actions canceled. Source subtask complete; **INPUT-005 OPEN**.

## Next handoff

When T5 coordinates one signed diagnostic Android candidate, record the immutable SHA and verify with physical mouse on POCO F5 Pro: app/window focus and menu transitions, ordinary edge swipes that temporarily show bars then return, OS Home/Back remain usable, no unintended app content resize, original keyboard/touch/wheel, landscape/Settings and world/save/exit/reopen. If bars remain permanently visible, obtain safe window SDK/visibility/status logging before changing Unity Player Settings. Do not claim READY or device acceptance from CI.

