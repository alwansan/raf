# T5 scope 20261109T1255Z-T5-scheduled-owner-gates-m7q2
origin=scheduled
baseline_sha=82f2f22ee700ee9c81af1ce325ae6f4f192ca1a6
experiment_key=T5-RESOLUTION-PROVENANCE-20261109
files=this work file and clients/T5/sessions/20261109T1255Z-T5-scheduled-owner-gates-m7q2.md
shared_resource=none; no Unity or game build; T4 mouse files excluded.

## Findings
- docs/DEVICE_FEEDBACK_42058825739_AR.md: world entry/save/reopen on run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628; failed delivery publish. Artifact IDs 13441227298 and signed checkpoint 13441766832 alone do not establish installed APK/OBB pair.
- docs/T5_RESOLUTION_ANDROID_POLICY_REVIEW_2026-11-05.md already records the right-side three buttons moved by acc964d0 and 96f41443. Do not duplicate; phone verification pending.
- GraphicsSettingsBox Android early return prevents desktop Screen.SetResolution but does NOT provide lower render resolution. Original menu binding/persistence and DynamicResolution.ResizeBuffers remain distinct; private IL trace required before a patch.
- LogRaft 220911-559: 23884 water pass errors, 3850 FFT errors, 1333 cursor RGBA32 warnings, one OBB GUID warning; 57 display-FPS samples average 22.29, min 3.02. 230108-327: 39132 water pass, 6026 FFT, two OBB GUID warnings, only two valid FPS samples. HUD 18.27 FPS/p95 82.82ms. Not paired same-scene benchmark or GPU timing.
- Shared Mini r3 CI42519487402 SUCCESS but Android15 SurfaceView PNG still unverified. r4 T5 NO_BUILD. T4 captured mouse source CI42518143297 SUCCESS, device pending.

## Next
1. Original ZIP2 pinned GraphicsSettingsBox menu binding/persistence IL identifiers and hashes, no raw game assets.
2. Pair APK manifest versionCode with OBB name/size/SHA from same signed checkpoint; label PACKAGE_UNMATCHED until proven.
3. Right-side button and Settings screenshot phone acceptance; preserve T4 files.
status=SOURCE_EVIDENCE_RECONCILED; DEVICE_PENDING; PACKAGE_UNMATCHED; NOT_READY.
