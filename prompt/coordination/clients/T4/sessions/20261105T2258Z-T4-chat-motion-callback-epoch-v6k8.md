# T4 chat — captured motion callback epoch guard

- session_id: 20261105T2258Z-T4-chat-motion-callback-epoch-v6k8
- origin: chat
- status: active
- base_sha: 27b2d7aca9228e56a678ffbbf2af37546735c97e
- resumed_from_sessions: 20261105T2241Z-T4-chat-immersive-bars-h8q2; 20261105T2235Z-T4-scheduled-u8k3; 20261105T2230Z-T4-chat-captured-mouse-sources-r7n5
- issue: INPUT-005
- work: prompt/coordination/work/INPUT-005/T4-20261105T2258Z-T4-chat-motion-callback-epoch-v6k8-callback-epoch.json
- experiment_key: T4-native-captured-PhysicalMouseMotionSource-AndroidJavaProxy-old-move-epoch-bound-v1-Unity2021-original0a6f0527
- resource_key: source-only-T4-original-ZIP2-managed-ABI
- intended_files: prompt/coordination/work/INPUT-005/T4-20261105T2258Z-T4-chat-motion-callback-epoch-v6k8-callback-epoch.json; prompt/coordination/clients/T4/sessions/20261105T2258Z-T4-chat-motion-callback-epoch-v6k8.md; android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs; android-port/Runtime/Platform/PhysicalMouseMotionSource.cs; android-port/Tests/PhysicalMouse/Program.cs; tests/test_t4_android_pointer_capture_policy.py; prompt/coordination/experiments/T4/20261105T2258Z-T4-chat-motion-callback-epoch-v6k8.json; prompt/coordination/B_TEAM/events/T4/20261105T2258Z-T4-chat-motion-callback-epoch-v6k8.json

## Distinct source finding and owner boundaries

Real existing `AndroidPhysicalMouseCapture.CapturedListener` was created once in `OnEnable` and returned `owner.RecordCapturedMotion(dx,dy)` where only `requested` is checked inside `captureGate`. Original UI pointer-release race source fix at `75bc6bda` guards a queued ReleaseCapture callback, **not** a previously queued captured-motion packet delivered after release/reacquire. An Android JNI listener callback could read a MOVE from an earlier request, then finish after a newer request increments `epoch`; with `requested=true`, stale delta could be injected into the new `Input.GetAxis` frame. This is a bounded source race hypothesis, **not a reproduced device incident**. Bind listener to request generation, never accept late events after release/reacquire. No touch, T5 controls, UI/Resolution, world/.rgd, audio or Unity full build changed.

Prior exact ZIP2 source ABI CI42121598304 and scheduled race CI42122830565 were SUCCESS; immersive CI42124859112 SUCCESS, all not actual on-device. Other active team runs at scope entry: [].

## Results

Pending.
