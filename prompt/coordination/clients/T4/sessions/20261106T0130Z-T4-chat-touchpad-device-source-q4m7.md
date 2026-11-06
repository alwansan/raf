# T4 chat — captured trackpad SOURCE_MOUSE / InputDevice SOURCE_TOUCHPAD

- session_id: 20261106T0130Z-T4-chat-touchpad-device-source-q4m7
- origin: chat
- status: active
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

Pending CI and source implementation.
