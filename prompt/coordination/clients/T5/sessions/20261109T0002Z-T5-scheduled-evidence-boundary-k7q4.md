# T5 scheduled — evidence boundary / device pairing
session_id: 20261109T0002Z-T5-scheduled-k7q4
origin: scheduled
issue_id: DISPLAY-003 / INPUT-005 / APK-OBB / PERF
experiment_key: t5-evidence-boundary-42058825739-vs-mini-v13-20261109
resource_key: none (no Unity/CI)
intended_files: this independent session note only
status: completed_source_review / DEVICE_PENDING

## Baseline and restored evidence
Owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md: game artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628; successful world enter/save/exit/reenter on phone; packaging publish failed. Report's 220911-559 LogRaft sample: 23,884 water pass errors, 3,850 FFT kernel errors, 1,333 cursor warnings, display estimator 57 samples mean 22.29, min 3.02. HUD screenshot 18.27 FPS and p95 82.82ms, separate measures. 230108-327: 39,132 water pass errors and 6,026 kernel errors, but only two valid display samples. Neither is a valid same-scene benchmark against a different build.

Unified mini lab shared round r4: v0.2.13-shared, package com.alwansan.raft.lab.shared, versionCode13, APK SHA256 6a41002cee345c48413ef56b0820211fb4ae73292229ec33ce830e82897194a7; CI42519487402 artifact13632379139. This is a **different app**, NOT the Raft game artifact; cannot pair its APK hash with Raft OBB or treat its GLSurfaceView measurements as Raft frame timings. T5-01 validates lab identity only. T5-02 needs owner-selected actual file through SAF; Android15 SAF denial is not OBB corruption. T5-03..06 remain manual.

## Executable decision criteria for next phone evidence
1. Pair *game* APK package/versionCode/cert/size/SHA with OBB basename main.<versionCode>.<game-package>.obb (and optional patch), size/SHA, actual mounted path, and same-run timestamp. Never substitute lab APK metadata. Missing accessible OBB means UNKNOWN, not corrupted.
2. Separate Unity in-game frame-time p50/p95 (ms) from LogRaft display FPS estimates and GPU busy; record source, sample count, elapsed interval, world/save, scene, rendering resolution, screen/window physical pixels, refresh rate and thermal condition. FPS from frame-time percentile is not percentile FPS by simple matching quantiles without inversion.
3. Compare water error **rate** as delta-count / observed seconds, not raw cumulative counts across unequal sessions. Associate window with world loading, game or menu. GPU unavailable must be literal unavailable.
4. Test right-side Show Xbox / Xbox layout / Test report with Android display cutout and gesture insets in menu, Settings, gameplay; verify click target and no clipping at both native and lower internal render scales. Keep game landscape, do not change mini-lab portrait.
5. Resolution choices must be separated into display mode/refresh, physical surface dimensions and internal render scale. Preserve aspect ratio and avoid PC Screen.SetResolution reflow. Source/UI repair and on-device acceptance remain unverified.

## Coordination / boundaries
T4 owns captured physical mouse button and wheel bridge; do not modify T4 source or repeat CI42518143297. T5 review is independent, no new build requested under shared r4 NO_BUILD, no claim of Android validation, no modification of original .rgd/assets. Prior T5 SAF regression CI42521743039 SUCCESS is source test, not phone APK/OBB proof.

Next: obtain latest CL/test manual T5-02..06 outputs and game manifest/digests, then perform paired attribution; if absent, prioritize isolated game-side Resolution/safe-area source repair with coordination before editing shared files.
