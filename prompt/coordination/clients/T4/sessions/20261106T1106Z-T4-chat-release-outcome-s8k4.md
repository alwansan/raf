# T4 chat — async Android pointer release outcome

session_id: 20261106T1106Z-T4-chat-release-outcome-s8k4
origin: chat
issue_id: INPUT-005 OPEN
status: completed_source_managed_ci_success_device_unverified
base_sha: c40742978308ce801054649b48383751f58858a4
resumed_from_sessions: 20261106T1042Z-T4-scheduled-f6n3; 20261106T1030Z-T4-chat-release-view-ownership-b7m4; 20261106T1014Z-T4-chat-owner-world-wire-parity-n7q3
work: prompt/coordination/work/INPUT-005/T4-20261106T1106Z-T4-chat-release-outcome-s8k4-native-release-outcome-telemetry.json
experiment: prompt/coordination/experiments/T4/20261106T1106Z-T4-chat-release-outcome-s8k4.json
event: prompt/coordination/B_TEAM/events/T4/20261106T1106Z-T4-chat-release-outcome-s8k4.json
handoff: prompt/coordination/discussions/INPUT-005/20261106T1106Z-T4-chat-release-outcome-s8k4-to-T5.md
experiment_key: T4-INPUT005-API26-pointer-release-actual-JNI-call-vs-skipped-UI-outcome-enum-privacy-safe-source-Unity2021ABI-v1
resource_key: T4-physical-mouse-source-only-dedicated-ci-no-unity-native

## Result

Prior [CI42204448436](https://github.com/alwansan/raf/actions/runs/42204448436) protected releasePointerCapture by original View identity; T4 scheduled 1042Z confirmed it and did not reimplement. The old physical_mouse_capture_released marker logs the Unity request BEFORE async UI dispatch, not a completed Android release. Source change [8f0b51a](https://github.com/alwansan/raf/commit/8f0b51a4ad710928937797b5352efc5893832f56) adds an independently useful diagnostic operation physical_mouse_capture_release_outcome with fixed result labels:
superseded_generation, unbound_request_view, focus_view_unavailable, focused_view_changed, target_not_captured, release_call_returned, jni_exception, ui_dispatch_exception.
Only labels are logged, no View identity, hash, pointers, exception text, game user paths or bytes. Noncritical logging is fail-soft. Its native_release_confirmed=false field is mandatory: even release_call_returned does NOT prove Android OS post-call capture state.

Production Java release policy, original epoch++ and generation guard, focused View ownership check, hasPointerCapture check, capture axis and input fallback remain unchanged. No per-frame diagnostics added. Preserve audio, Settings, touch and original game save files; no full Unity/player build or APK/OBB published by T4.

## Tests

Intermediate [CI42208627456](https://github.com/alwansan/raf/actions/runs/42208627456) failed two old lexical tests that required inline if(...) return syntax, not a proven runtime regression. Updated tests/test_t4_android_pointer_capture_policy.py by commit [e06566a](https://github.com/alwansan/raf/commit/e06566a7e72f6128252e2a974e66af46ca57bac3) after extending the work scope: same epoch predicate, log superseded, then return BEFORE any JNI release. The existing view-identity test was adapted and received one new telemetry regression test. No weakening of the underlying stale callback check.

Final exact [CI42208882663](https://github.com/alwansan/raf/actions/runs/42208882663) COMPLETED SUCCESS on e06566a7, job 127862302416: Python 7 original route +7 axis patch +21 capture policy +5 mouse presence +7 view identity/outcome = 47/47. Managed captured-motion executable and original Unity2021 DLL ABI CSharp compile passed; private immutable original code/DLL hash gate and patch staging passed. Separate platform [CI42208627329](https://github.com/alwansan/raf/actions/runs/42208627329) SUCCESS on source implementation 8f0b51a. No Android device run, native Unity IL2CPP build, or new signed APK+OBB; do not claim playability or actual mouse success.

## Next

T5 deliver one immutable signed APK+matching OBB with exact source SHA/versionCode and hashes. Owner POCO F5 Pro with physical mouse/keyboard: verify menu vs game cursor, 360-degree camera, focus/home/pause/reconnect, then correlate requested, release_outcome, view_changed, lost and relative mouse markers. This will discriminate old View OS auto-release from incomplete focus transition. Recheck world save, terminate process, reopen same world and progress; old artifact42058825739 owner confirmation and separate original managed 7/7 byte-equivalence CI42201568118 are not newer-device proof. INPUT-005 OPEN; LOCAL-005 OPEN; NOT_READY 0/3. No team jobs cancelled.
