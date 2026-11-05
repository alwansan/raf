# T4 chat — captured motion callback epoch guard

- session_id: 20261105T2258Z-T4-chat-motion-callback-epoch-v6k8
- origin: chat
- status: completed_source_integrated_device_unverified
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

## Implemented, authenticated source results

- Code: [PhysicalMouseMotionSource.cs helper commit f3c2abb2](https://github.com/alwansan/raf/commit/f3c2abb20abcc967e20fa7ca03595469a3054e1b) adds `AcceptEpoch(listenerEpoch,activeEpoch,requested)`. [AndroidPhysicalMouseCapture.cs commit a5d3ce04](https://github.com/alwansan/raf/commit/a5d3ce04e59a0734b689c610da5f65dad8a4b117) creates a distinct AndroidJavaProxy `CapturedListener(this,currentEpoch)` **for each native capture request**, installs that exact listener, prefilters old generation on JNI callback and rechecks under `captureGate` in `RecordCapturedMotion(int listenerEpoch,...)` before recording relative data. A stale onCapturedPointer ACTION_MOVE cannot be transferred to a new request merely because `requested` becomes true again. Preserves T4 scheduled `releaseEpoch` fix (commit75bc6bda), input-system source filtering, touch, camera legacy GetAxis, world/save, T5 UI/Resolution and original asset metadata.
- Executable C# test additions: six independent generation acceptance/rejection assertions in `android-port/Tests/PhysicalMouse/Program.cs`, [commit f18d6bec](https://github.com/alwansan/raf/commit/f18d6becbb8543e0cbb45420e28cf2f3e81463bf). Python source policy adds three tests asserting per-request proxy construction, listener token propagated, final token recheck under shared capture lock, and prior release-epoch guard retained; [commit 2be085c3](https://github.com/alwansan/raf/commit/2be085c362c8c3f0dd57c1c4a94ec5991174b1e4). Two older source assertions depended on obsolete signature/comment text and were strengthened to current generation-aware signature without removing safety checks; [commit bbcc0560](https://github.com/alwansan/raf/commit/bbcc0560f3f784c6b224994771086588522b3f13).
- **Final CI:** [42126395609](https://github.com/alwansan/raf/actions/runs/42126395609) **COMPLETED SUCCESS**, job127591581668, immutable source `bbcc0560f3f784c6b224994771086588522b3f13`. **7+7+18 = 32 Python controls**, **36 C# .NET frame/source and generation controls**, genuine original Unity2021 Android managed C# compilation, and exact private original ZIP2 DLL SHA/size plus ILSpy rewrite of **4 Mouse X, 4 Mouse Y, 2 Cursor.lockState sites across five original source files**, no private original source output published. Intermediate runs 42126170243, 42126238081 and 42126279302 failed as expected while static tests still referenced old method signature/comment; final passing commit supersedes them.
- **Limitations:** source inspection race hypothesis, not actual Android device repro; Unity managed-ABI compilation != native Unity IL2CPP APK. Device focus, black pointer, system bars, physical mouse/wheel, touch/controller, new signed candidate and original world/save/reopen remain unverified. Owner's successful playable-world/save/reopen on artifact42058825739 is for older SHA, not the current changes. **INPUT-005 OPEN; NOT_READY 0/3**.
- **No work interference:** no heavy Unity/APK run or native request/cancel, no T5 controls, audio/Settings, touch layout, .meta GUID or .rgd mutations.

## Next chat/scheduled T4

For a T5-coordinated new signed Android APK+OBB of exact source SHA, test fast menu/game/menu transitions while moving a real physical mouse; verify old capture callbacks do not induce camera jumps after recapture, the original Raft menu pointer works, Android transient bars preserve OS swipes, mouse buttons/wheel and external keyboard/touch remain, and game world/save/full exit/reopen remain reliable. Use bounded logs (`physical_mouse_capture_requested/lost/relative/released`) and exact signed package manifest. Source-only CI is not phone acceptance.


