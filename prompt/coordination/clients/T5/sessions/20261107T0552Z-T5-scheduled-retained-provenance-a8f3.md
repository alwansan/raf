# T5 scheduled session 20261107T0552Z-T5-scheduled-retained-provenance-a8f3

origin: scheduled

scope_commit: 95ffba2f76064e3c51300ee6faf0f1c885149dc2

origin_source_sha: 7e607e44942aca3b61d4c616c14a204ef63a4c5b

resumed_from: 20261107T0450Z-T5-scheduled-artifact-identity-p4n8.md

## Live evidence (2026-11-07 05:52 UTC)

Owner phone success belongs only to native run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628.

API /actions/runs/42058825739/artifacts: signed checkpoint 13441766832, size 2974110506 bytes, expires 2026-11-07T18:18:17Z, expired=false; original delivery 13441227298 absent.

NEW: API /actions/runs/42110297871/artifacts confirms retained delivery artifact 13454900880, name t5-retained-native-delivery-42058825739, size 5948243834 bytes, digest sha256:41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef, expires 2026-11-08T21:12:40Z, expired=false. Retention workflow head df6144411a130cc1ac23f1df4ae7f653d61e9704 is NOT native source SHA.

API /actions/runs/42296450023/artifacts: newer checkpoint 13550196498 expires 2026-11-09T23:48:15Z, newer delivery 13549514149 expires 2026-11-09T23:49:06Z. Native source a1737bd736e276d53df808442cfae3b1eea0d488 differs from phone-tested source.

## Boundaries and next step

The retained copy prevents assuming total loss of old delivery today, but its internal APK/OBB binary identity is NOT proven. Outer artifact ZIP digest is NOT APK/OBB SHA. No downloaded ZIP, signer/versionCode, phone installation, LogRaft new performance sample, UI modification, CI, Unity or Release performed.

Preserve signed checkpoint before 2026-11-07T18:18:17Z and retained delivery before 2026-11-08T21:12:40Z in durable authorized storage. Validate delivery.json, APK signer/versionCode, OBB filename/size/SHA and original build manifest. Do not trigger duplicate native build. T4 owns physical mouse; T5 UI scope still pending. Full readiness NOT_READY 0/3.
