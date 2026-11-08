# T5 20261108T0750Z-T5-scheduled-artifact-provenance-a83c
origin: scheduled
base_sha: b7a9c614bdf1069da98264cf17bb598cef8f1a01
scope_commit: c09fcdfd8a41c058ab18935e091c4cd06ae1ecfe
resumed_from: clients/T5/sessions/20261108T0650Z-T5-scheduled-ci-provenance-91ac.md
owner_report: docs/DEVICE_FEEDBACK_42058825739_AR.md
issue: APK/OBB provenance, read-only Actions investigation

## Verified 2026-11-08 ~07:50 UTC
- Original run 42058825739 source e9c358eda01785b65e4eb14f18723da426635628. Current artifact list has four small staging artifacts only (833, 1990, 3242, 2095 bytes), not original delivery ZIP; historical artifact IDs may have expired.
- Rescue run 42110297871 pinned-artifact-rescue completed SUCCESS; artifact 13454900880 t5-retained-native-delivery-42058825739 size 5,948,243,834 bytes, expired=false, expires 2026-11-08T21:12:40Z. Approximately 13h22m remain at inspection. Retention is urgent.
- Run 42281310905 artifact list contains tiny staging outputs only, no new APK/OBB/XAPK.
- Trial vote round trial-20261106-r1 has T4 needs, four others do not; no consensus. No native build requested.

## Limitations and next
- GitHub artifact ZIP size does not establish APK/OBB SHA256, versionCode or installed identity. No device hashes were obtained.
- Preserve rescue artifact before 2026-11-08T21:12:40Z in authorized private storage after quota check; stream-verify SHA256/manifest. Do not publicly republish raw game content.
- Compare signed checkpoint APK package/versionCode and OBB filename/size/SHA with device-side installed hashes; only then associate LogRaft FPS with that package.
- No change to T4 mouse, T5 UI/Resolution, native request, CL or Unity; no phone/GPU claim.