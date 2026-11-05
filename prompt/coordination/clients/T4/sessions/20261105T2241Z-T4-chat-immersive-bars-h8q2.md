# T4 chat — Android system-bar immersive guard

- session_id: 20261105T2241Z-T4-chat-immersive-bars-h8q2
- origin: chat
- status: active
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

Pending.
