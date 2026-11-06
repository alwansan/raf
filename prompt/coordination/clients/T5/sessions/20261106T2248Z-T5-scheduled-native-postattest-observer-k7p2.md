# T5 scheduled — immutable native build provenance checkpoint

- session_id: 20261106T2248Z-T5-scheduled-native-postattest-observer-k7p2
- origin: scheduled
- owner: T5
- issue_id: DELIVERY-013 / INTEGRATION-001
- resumed_from_sessions: 20261106T2229Z-T5-chat-native-package-postattest-c61b; 20261106T2150Z-T5-scheduled-native-reconstruct-8b4f
- base_sha: 0346399e628e0303cf68b3f514c383a05d749b8c
- scope_commit: df46122adab620aa2b4144fa050ed0cfcce99e30
- status: waiting_ci
- experiment_key: native-42296450023-a1737bd-reconstruct-observe-vs-f68af818-postattest

## Live checks (2026-11-06 22:48 UTC)

Owner report docs/DEVICE_FEEDBACK_42058825739_AR.md confirms world entry/save/reopen on old artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628 only. CL session 220911-559 summary reports 23,884 water pass errors, 3,850 FFT errors and 57 display FPS samples averaging 22.29; no device GPU timing or SHA proof of installed APK/OBB.

GitHub native run https://github.com/alwansan/raf/actions/runs/42296450023 remains in_progress on immutable a1737bd736e276d53df808442cfae3b1eea0d488; native-request-gate and unity-license-preflight completed successfully; reconstruct currently in Unity Editor 2021.3.45f2 Android import and compile. This predates source-only verified packaging postattestation f68af8185665d17d98fc13ea7f95b325c258d82f (CI42305389897 green 3/3, A3 packaging CI42305389870 green). Therefore even if the running build completes, do not claim it exercised the later cross-delivery verifier.

Current branch HEAD before scope commit was 0346399e628e0303cf68b3f514c383a05d749b8c. Latest T5 chat session already owns and completed postattestation source files; this scheduled cycle uses separate read-only observation scope. Trial r1 remains T4 yes, T1/T2/T3/T5 no; owner's independent direct build request is separately documented, not team consensus.

## Boundaries and next action

No Unity dispatch/cancel, no original asset export, no APK/OBB download, no changes to mouse/Resolution/three buttons or teammate source. This checkpoint is a live provenance distinction, not new device acceptance or performance measurement. Next poll native run until terminal; if failed identify exact failing step/log; if succeeded inspect actual artifact manifest, APK signature/versionCode, OBB name/size/SHA and XAPK nested bytes, explicitly noting source postattestation absent. Maintain NOT_READY 0/3.
