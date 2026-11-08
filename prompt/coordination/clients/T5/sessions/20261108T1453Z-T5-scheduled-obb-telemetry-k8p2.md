# T5 scheduled checkpoint — 20261108T1453Z-T5-scheduled-obb-telemetry-k8p2

- origin: scheduled
- base_sha: ee63cb4d9aed3331118581605e61df42d351f9b5
- scope_commit: 37b351e389faf299c76e7cb0241097c4e3923213
- implementation_commit: 946d11dcc3690470e5a20bcd0f58d455b30c41bd
- resumed_from: prior T5 scheduled signed-pair extraction/LogRaft CI results; owner report docs/DEVICE_FEEDBACK_42058825739_AR.md and newer apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md
- origin evidence: owner confirmed world/save/reopen on 42058825739 (e9c358eda01785b65e4eb14f18723da426635628) only. New 8 Nov report: pointer camera capture works, physical buttons and wheel fail (T4 scope), water errors 74359, FFT 11165, cursor warnings 7372; SurfaceFlinger 83 samples avg 47.90 is not Unity FPS; GPU busy 88 samples avg 71.43% is not per-game GPU utilization.
- deliverable: apk-for-testing/examples/t5-package-telemetry-testpack.json, 6 data-only cases: signed APK SAF SHA, main OBB SAF SHA, patch/main warnings, resolution/frame-time, GPU/error correlation, right-side UI acceptance.
- verification: JSON assembled with 6 unique IDs, permitted test types, required keys, no asset/code fields, 3403 bytes (<64KiB); no full validator execution, CI or Android host APK build claimed.
- overlap: T4 retains physical mouse buttons and scroll; no edits to T4, Unity, .meta, .rgd, or game runtime. Mini-host is SOURCE_READY only. No 5/5 full-XAPK vote changes.
- remaining: run scripts/validate_android_testpack.py on the committed pack in CI or local checkout, exercise import on a built mini-host, obtain real SAF-selected file digests and installed package evidence, then compare owner APK/OBB; integrate resolution/right-side controls in game after source ownership check; match LogRaft intervals and render scale on device.
- readiness: NOT_READY 0/3; no device claims from this testpack.
