# T3 scheduled — local particle Material PPtr anchor validation

- session_id: `20261108T1733Z-T3-scheduled-local-material-resolve-n5q8`; origin: `scheduled`; issue: RENDER-002 OPEN / NOT_READY.
- resumed_from: `20261108T1631Z-T3-scheduled-null-guid-h6p4` and `20261108T1556Z-T3-chat-particle-ci-c83f`.
- initial base_sha: `2af4d80f7509f90f8c4d20b5ac80f4f598f1e499`.
- scope registered first at `b7f4fe7c`: `prompt/coordination/work/RENDER-002/20261108T1733Z-T3-scheduled-local-material-resolve-n5q8.json`.
- confirmed previous null-GUID regression [CI42500307383](https://github.com/alwansan/raf/actions/runs/42500307383) **SUCCESS** on test commit `16d8e190`; not a device graphics result.
- new source patch: `b2e06c1f`, corrected regex anchor capture `506b9324`; test `eb624219`, fixture newline correction `7dc8bc19`. Positive local Material PPtrs are now checked against same-YAML document anchors and Unity class 21, with separate valid, missing, wrong-class and duplicate-anchor counters. This is a stricter structural audit than previously counting all positive local IDs as valid.
- Verification status: source patch and fixture published; new exact-head CI not yet verified. Existing source-only CI may run automatically; do not launch equivalent jobs. The new fixture uses a synthetic Unity YAML document only.
- Device feedback [5 Nov](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md): world/save/reentry succeeded on artifact 42058825739, but white raft/hand and square smoke remain. [8 Nov](https://github.com/alwansan/raf/blob/feature/android-native-port/apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md): physical mouse camera capture works but clicks/wheel fail; water/FFT errors remain.
- Scope boundary: no real ZIP2 particle source/export or CL pixels analyzed in this run; no game resource, GUID, shader, Android mini APK or XAPK modified. T4 owns mouse, T1/T2 water, T5 distribution/resolution.
- Next: verify exact-head Python CI, then run audited original-to-export particle renderer material chain against authenticated ZIP2 in isolated workflow; inspect Shader/Texture/Blend/Alpha and compare owner images before any game asset fix. Avoid treating synthetic pass as pixel proof.
