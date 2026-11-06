# T4 chat — Android currentActivity null lifecycle safety

- session_id: `20261106T1304Z-T4-chat-null-activity-p7h2`; origin: `chat`; status: `active`
- base_sha: `6e498046b70129bfa255e248fc65292818f966fe`
- resumed_from_sessions: `20261106T1237Z-T4-scheduled-x5p9`, `20261106T1128Z-T4-chat-device-mouse-release-evidence-p8m2`
- work: `prompt/coordination/work/INPUT-005/T4-20261106T1304Z-T4-chat-null-activity-p7h2-android-activity-null-guard.json`
- issue: INPUT-005 OPEN; LOCAL-005 latest owner phone confirmed only at artifact 42058825739
- experiment_key: `T4-INPUT005-android-unityplayer-null-currentActivity-safe-dispatch-UI-probe-request-release-Unity2021-managedABI-v1`
- resource_key: `T4-mouse-managed-source-only-no-Unity-build`

## Reserved scope before code
Inspect `AndroidPhysicalMouseCapture.OnAndroidUi` and UI callbacks for missing `UnityPlayer.currentActivity`: a null Java Activity currently risks unhandled `NullReferenceException` on focus loss/destroy despite AndroidJavaException-only fallback. Add narrow explicit null guard, preserve UI thread Java operation, capture generation and fixed outcome labels; add synthetic structural tests to existing source-only suite. No input axis mapping, touch, HUD, game source, Save/Load, original binary, other agent files, Unity game build or actual phone claim. Other T4 cross-process original RGD work is isolated.

## Evidence baseline
- Owner 5 November physical phone world/create/save/reopen: [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) source `e9c358eda01785b65e4eb14f18723da426635628`; **does not** contain post-build mouse telemetry.
- Latest mouse native source CI [42208882663](https://github.com/alwansan/raf/actions/runs/42208882663): 47/47 source tests and Unity2021 managed compile; no Android runtime.
- Latest mouse log verifier CI [42210561898](https://github.com/alwansan/raf/actions/runs/42210561898): 22/22 source only.
- T1 run [42221700354](https://github.com/alwansan/raf/actions/runs/42221700354) in_progress at inspection; do not cancel.

## Next step
Implement targeted guard and test, verify C# original managed ABI and CI, record resulting SHA/status and limitations in this session. Do not write state.json/MEMORY.md belonging to possibly concurrent T4 sessions.
