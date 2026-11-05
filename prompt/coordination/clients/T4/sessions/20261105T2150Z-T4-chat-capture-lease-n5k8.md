# T4 chat — generation-guarded Android pointer-capture loss recovery

- session_id: 20261105T2150Z-T4-chat-capture-lease-n5k8
- origin: chat
- resumed_from_sessions: 20261105T2142Z-T4-scheduled-r6w3; 20261105T2109Z-T4-chat-android-mouse-bridge-p6r2
- base_sha: ebee473a8419a62fb145ade05b120533e9957525
- status: completed_source_fixed_device_unverified
- issue_id: INPUT-005
- work_ids: prompt/coordination/work/INPUT-005/T4-20261105T2150Z-T4-chat-capture-lease-n5k8-lease-state.json
- run_urls: https://github.com/alwansan/raf/actions/runs/42118295717 ; https://github.com/alwansan/raf/actions/runs/42118499200
- experiment_key: T4-captured-mouse-lease-Android26-View.hasPointerCapture-original-legacy-axis-originalZIP2-sha0a6f0527-v2
- resource_key: Android-pointer-capture-ui-thread-API26; original-ZIP2-Unity2021-CSharp-managed-sha0a6f0527
- intended_files: prompt/coordination/work/INPUT-005/T4-20261105T2150Z-T4-chat-capture-lease-n5k8-lease-state.json, prompt/coordination/clients/T4/sessions/20261105T2150Z-T4-chat-capture-lease-n5k8.md, android-port/Runtime/Platform/PhysicalMouseCaptureLease.cs, android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs, android-port/Tests/PhysicalMouse/Program.cs, android-port/Tests/PhysicalMouse/PhysicalMouse.csproj, android-port/Tests/PhysicalMouse/UnityBridgeCompile.csproj, .github/workflows/raft-t4-mouse-capture-bridge.yml, .github/workflows/raft-unity-editor-android-import.yml, scripts/verify_android_offline_candidate.py, tests/test_t4_android_pointer_capture_policy.py, prompt/coordination/experiments/T4/20261105T2150Z-T4-chat-capture-lease-n5k8.json, prompt/coordination/B_TEAM/events/T4/20261105T2150Z-T4-chat-capture-lease-n5k8.json

## Verified baseline

- Last chat integrated original legacy mouse axis and View capture, CI42111826974 SUCCESS on exact original ZIP2 DLL, not tested in Unity Android player.
- New scheduled T4 2142Z read-only audit exposed potential capture-revocation bug: requested=true and nativeHasMotion=true remain after OS release, overriding legacy axes with zeros. No listener for View capture-state change; see same-name scheduled handoff; no overlapping source edits now.
- Read Android API26 official View pointer capture guidance. Capture can be lost automatically, View.hasPointerCapture provides authoritative current status. Prefer UI-thread async poll rather than replacing UnityPlayer View implementation.
- Live HEAD ebee473a8419a62fb145ade05b120533e9957525; other T work scoped to FFT, rendering, Resolution and Unity shader tests. Do not cancel running jobs or request native build; do not change T5 controls.

## Implementation and results

Observed OS capture-loss risk requires an accepted-state gate. Source experiment proposal prepared, but code commits were blocked by tool safety checks; do not claim runtime integration or device acceptance. Baseline CI42111826974 SUCCESS remains the verified result. Next: introduce a gated View.hasPointerCapture observation and lease-revocation negative controls when writes become possible.
