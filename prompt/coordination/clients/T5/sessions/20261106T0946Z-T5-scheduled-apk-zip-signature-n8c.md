# T5 scheduled checkpoint — 2026-11-06 09:46 UTC
session_id: 20261106T0946Z-T5-scheduled-apk-zip-signature-n8c
origin: scheduled
base_sha: 8e67a3be6a49e0f28adc918210ffeec72cfa28aa
resumed_from_sessions: 20261106T0751Z-T5-scheduled-apk-archive-coverage-c81.md; 20261106T0654Z-T5-scheduled-pair-ci-a7k2.md
scope_file: prompt/coordination/clients/T5/work/20261106T0946Z-T5-scheduled-apk-zip-signature-n8c.md
issue_id: INTEGRATION-001
status: waiting_ci

## Verified source fix
- Existing CI42183679266 on a14d9f1 failed at synthetic-pair-check, while previous 42170921976 passed 21 tests before two APK archive regressions were added.
- Inspected test source: APK encrypted-flag fixture searched literal b\"PK\\\\x03\\\\x04\" and b\"PK\\\\x01\\\\x02\", unlike working OBB test's actual byte escapes. Thus assertion fails before verifier's encrypted-flag guard.
- Scope commit c2f399ebe1fa749c93f68fb21c2ebd729f01c601; repaired both byte signatures in tests/test_t5_verify_apk_obb_pair.py at commit 59bd64512487cf1596ad627bd039662c61403b87. No production verifier, Unity, Android, assets, Settings, mouse, delivery or shared CI changes.
- New push-triggered workflow should run automatically. Do not dispatch equivalent duplicate; inspect resulting CI after queue drains.

## Evidence and limits
- Owner phone world/save/reentry only on artifact 42058825739, source e9c358e; not attributable to this test fix.
- Original CL 220911 sample: 23,884 water pass failures, 3,850 FFT kernel failures, 57 external FPS samples mean 22.29; 230108 2 valid external FPS only. No new LogRaft device measurement.
- Real signed APK/OBB versionCode/size/SHA and optional patch GUID remain separate verification task; this fix is synthetic only.
- Next: verify all 23 unit cases on new CI, then match original signed pair to delivery manifest if artifact retrieval possible; preserve NOT_READY 0/3.
