# T5 scheduled checkpoint
session_id=20261109T1655Z-T5-scheduled-obb-path-f83c
origin=scheduled
resumed_from_sessions=20261109T1552Z-T5-scheduled-obb-guid-regression-c4e9,20261109T1356Z-T5-scheduled-artifact-run-scope-n4q8
base_sha=6611d62b7b1df6c3fcd576fead03e2b1ee713f25
scope_commit=fad0e84eedd99e1c3597dda72d008f5a34f24b75
source_commit=8791e8be65e68fcb792f4c4b6d4672dceee09e2e
regression_commit=fd2419583e11cfe9aba02b3f20c3fa17623a58e4
originating_report=docs/DEVICE_FEEDBACK_42058825739_AR.md
work=prompt/coordination/T_TEAM/work/20261109T1655Z-T5-scheduled-obb-path-f83c.md

## Result
Read owner phone feedback, AGENTS, current protocols, current branch head and recent Actions. Found reproducible logic error in read-only OBB GUID classifier: suffix-only regex would treat a fake path under /tmp/Android/obb as an installed expansion OBB. Restricted match to canonical /storage/emulated/<id>/Android/obb and /sdcard/Android/obb roots, and added two regression methods for spoofed paths and sdcard alias. The existing six tests from prior session were preserved. No source assets, T4 mouse files, Unity builds or signed delivery were modified.

## Verification and limits
Code inspection confirms the before/after regex behavior, but new tests have NOT been executed in Python or CI. Do not mark as test-PASS. Prior CI 42657856705 and 42657857161 completed success for other checks, not these tests. No phone testing, new CL cohort measurements, actual APK/OBB SHA verification or Resolution device proof. The device world/save/re-entry is owner-confirmed only for artifact 42058825739. Right-hand button source changes are pending device confirmation. NOT_READY.

## Next
Run python -m unittest scripts.test_t5_obb_guid_contract on full checkout, then use exact signed delivery.json with raw LogRaft logs to distinguish main and optional patch; coordinate Resolution with original Settings binding and T4 mouse independently. If tests fail, repair without repeating Unity build.
