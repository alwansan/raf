# T4 scheduled checkpoint — 20261108T0336Z-T4-scheduled-ci-verified-h8p3
origin: scheduled
resumed_from_sessions:
- 20261108T0237Z-T4-scheduled-retry-classifier-gap-n4q8
- 20261108T0142Z-T4-scheduled-retry-ci-r7m2
base_sha: c1a3fe3990239a43c26806614e29d79cf8e50d47
scope_commit: 0fceef42e7b4500cc722ead2038de84c04bf8655
issue_id: INPUT-005
status: completed (CI evidence verification only)

Read owner feedback 5 November and current T-team operating instructions. Confirmed 42058825739 source e9c358ed is the *only owner-confirmed* world/save/exit/reopen device case; publishing failed separately. Inspected current branch and latest Actions: [42439391089](https://github.com/alwansan/raf/actions/runs/42439391089) SUCCESS on 8e7fc89a, including classifier-source-only Verify source-only classifier regression suite; preceding [42439389712](https://github.com/alwansan/raf/actions/runs/42439389712) SUCCESS on 4e80e762. These validate the new retry-window parser regressions from previous session; no need to duplicate CI. Neither establishes camera relative movement, black system cursor suppression, Raft cursor behavior or keyboard compatibility on Android. No source runtime changes this cycle. No change to .rgd, shaders, Settings, T5 UI or Resolution. No Unity run launched. No overlap with T5. CL screenshots and logger session links remain pinned in docs/DEVICE_FEEDBACK_42058825739_AR.md; no newer physical_mouse_capture_retry device evidence demonstrated. Next: correlate new APK source SHA with actual on-device logs containing retry/epoch/release events and investigate Android requestPointerCapture callback behavior, while preserving keyboard and menu release.

work: prompt/coordination/work/20261108T0336Z-T4-scheduled-ci-verified-h8p3.md
