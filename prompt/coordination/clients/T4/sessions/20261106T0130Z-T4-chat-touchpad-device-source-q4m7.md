# T4 chat — captured trackpad SOURCE_MOUSE / InputDevice SOURCE_TOUCHPAD

- session_id: 20261106T0130Z-T4-chat-touchpad-device-source-q4m7
- origin: chat
- status: completed_source_integrated_device_unverified
- base_sha: 797174cc02e14aef3f115a5917730a4068623c75
- issue_id: INPUT-005
- work: prompt/coordination/work/INPUT-005/T4-20261106T0130Z-T4-chat-touchpad-device-source-q4m7-device-source.json
- resumed_from_sessions: 20261106T0035Z-T4-scheduled-k9m2; 20261105T2258Z-T4-chat-motion-callback-epoch-v6k8; 20261105T2241Z-T4-chat-immersive-bars-h8q2
- experiment_key: T4-official-Android-InputDevice-SOURCE_TOUCHPAD-from-getSources-MotionEvent-SOURCE_MOUSE-API26-Unity2021-ZIP2-15964ea8-v1
- resource_key: bounded-source-only-unity-managed-abi-0a6f0527856a-no-real-player
- intended_files: prompt/coordination/work/INPUT-005/T4-20261106T0130Z-T4-chat-touchpad-device-source-q4m7-device-source.json; prompt/coordination/clients/T4/sessions/20261106T0130Z-T4-chat-touchpad-device-source-q4m7.md; android-port/Runtime/Platform/PhysicalMouseMotionSource.cs; android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs; android-port/Tests/PhysicalMouse/Program.cs; tests/test_t4_android_pointer_capture_policy.py; .github/workflows/raft-t4-mouse-capture-bridge.yml; prompt/coordination/experiments/T4/20261106T0130Z-T4-chat-touchpad-device-source-q4m7.json; prompt/coordination/B_TEAM/events/T4/20261106T0130Z-T4-chat-touchpad-device-source-q4m7.json

## Proven baseline

T4 scheduled 0035Z removed misleading legacy Input.mousePresent guard, source commit24ee5002, tests 8a3de6f. CI42138014394 SUCCESS on source, but scheduled presence-specific static tests not part of that workflow. Earlier chat CI42126395609 SUCCESS source-only for listener generation and original Unity managed ABI; no physical device test. T5 owns Resolution/UI, T1/T2/T3 handle water/materials. No native game build dispatched or original game metadata touched.

## Distinct official Android input-contract finding

On Android, touchpads advertise SOURCE_MOUSE|SOURCE_TOUCHPAD via InputDevice.getSources(), but MotionEvent.getSource() normally reports only SOURCE_MOUSE for their events (Android InputDevice reference). Existing PhysicalMouseMotionSource.Classify(eventSource) checks SOURCE_TOUCHPAD in eventSource and ignores SOURCE_MOUSE; so a captured touchpad event with eventSource=SOURCE_MOUSE is classified Ignore. This is a **verified API mismatch and code-level unreachable branch under documented usual events**, not observed on POCO F5 Pro. Fix must consult the actual event's InputDevice capabilities without interpreting ordinary touchscreen/mouse absolute coordinates as camera deltas.

## Results

## Verified source integration and CI

- **Official Android input contract:** `InputDevice.SOURCE_TOUCHPAD` docs explicitly state that trackpads report `SOURCE_MOUSE | SOURCE_TOUCHPAD` from `InputDevice.getSources()` but `MotionEvent.getSource()` normally reports only `SOURCE_MOUSE`. The previous `PhysicalMouseMotionSource.Classify(source)` discarded that common trackpad MOVE event even when View already had pointer capture. Official docs: https://developer.android.com/reference/android/view/InputDevice#SOURCE_TOUCHPAD.
- **Implemented (Android-only, fail open):** [b968375c](https://github.com/alwansan/raf/commit/b968375ceec98136cbef437ecbb53589bc9a62ec) adds `Classify(int eventSource,int deviceSources)`; SOURCE_MOUSE=8194 and device advertised SOURCE_TOUCHPAD=1048584 must both match. Direct SOURCE_MOUSE_RELATIVE=131076 stays old Mouse path; SOURCE_TOUCHSCREEN and ordinary mouse remain ignored. [bf0f3232](https://github.com/alwansan/raf/commit/bf0f32326952ff5c4ff44e5df168ef1c701eb942) calls `InputEvent.getDevice().getSources()` only on captured SOURCE_MOUSE; scoped JNI wrapper disposed, missing device -> original Unity fallback; existing captured listener generation, 64 history bound and original legacy Mouse X/Y preserved.
- **Tests and integration:** [8253bd7f](https://github.com/alwansan/raf/commit/8253bd7fdd09730c6bfd79a57fcc51968d872cf5) adds 12 executable .NET source/device positive+negative guards, [1451e81e](https://github.com/alwansan/raf/commit/1451e81ed9649f8266b46aef0afd4c4f9ba844fe) adds three Python source controls, [bc64aa8c](https://github.com/alwansan/raf/commit/bc64aa8ceb4c7445d8910e5bf140b0a749ad4261) includes the scheduled T4 five-case `tests/test_t4_physical_mouse_presence_policy.py` in existing isolated original source/ABI workflow. The last assertion update [f0e6cfd6](https://github.com/alwansan/raf/commit/f0e6cfd60761195ff38292b2b6765e029df051c6) changes the prior one-argument policy assertion to the real two-argument contract; no safety assertions removed.
- **CI:** [42144434260](https://github.com/alwansan/raf/actions/runs/42144434260) **COMPLETED SUCCESS**, job127652374706, immutable source SHA `f0e6cfd60761195ff38292b2b6765e029df051c6`: **7 original routing +7 exact patch +21 capture source policy +5 scheduled presence = 40/40 Python**, **48/48 executable .NET mouse/source/motion checks**, compilation of real `AndroidPhysicalMouseCapture.cs` against authenticated original Unity2021 Core/AndroidJNI/InputLegacy/InputSystem libraries **PASS**, private original ZIP2 Assembly-CSharp.dll SHA/size exact gate and ILSpy rewrite **4 Mouse X +4 Mouse Y +2 cursor assignments across five private original source files PASS**. Intermediate CI42144331049 and CI42144368616 failed because obsolete static test expected `Classify(source)`; corrected and final run green. No original game bytecode/source artifact published.
- **Cooperation and limits:** T4 scheduled 0035Z physical presence code and its exclusions kept unchanged, now regression tested in final CI. No T5 UI/Resolution, T1–T3 shaders/water, keyboard/touch, FMOD or `.rgd` modifications. No full Unity Editor/IL2CPP native build/release requested or Actions canceled. This resolves an official API source-routing bug in source, **not** verified hardware pointer capture. `INPUT-005` remains OPEN; project **NOT_READY 0/3**. Original phone world/save/exit/reopen acceptance on artifact42058825739 older immutable SHA remains bounded to that device version only.

## Next T4 and T5 handoff

Once T5 coordinates a signed native candidate, verify source SHA and matching APK/OBB manifest; use an external touchpad if available, record **safe source-category counts only**, test captured relative trackpad motion (MotionEvent SOURCE_MOUSE / device SOURCE_TOUCHPAD), full real USB/Bluetooth mouse and camera unlimited turn, original button/wheel/keyboard/LEFT-touch, quick menu→game transitions, capture loss/disconnect, OS system bars/black pointer, and playable local world/save/full-exit/reopen on exactly the same new version. If Android `getDevice()` is null on a vendor or built-in touchpad, this deliberately returns to original Unity handling; diagnose real hardware before bypassing class checks. No unverified success flags or device claims.


