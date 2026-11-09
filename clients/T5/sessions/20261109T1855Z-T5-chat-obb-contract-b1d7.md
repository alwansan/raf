# T5 chat — OBB GUID regression execution
session_id=20261109T1855Z-T5-chat-obb-contract-b1d7
origin=chat
base_sha=3aa107eec32e14c06454075ad069b49a9302606c
resumed_from_sessions=20261109T1655Z-T5-scheduled-obb-path-f83c,20261109T1750Z-T5-scheduled-obb-json-a9e4
work=work/T5/20261109T1855Z-T5-chat-obb-contract-b1d7.md
scope=Source-only CI verification of existing OBB GUID exact-root and unique-delivery-JSON tests. Do not edit classifier/test files while scheduled work may touch them.
intended_files=.github/workflows/raft-t5-obb-guid-contract-regression.yml,work/T5/20261109T1855Z-T5-chat-obb-contract-b1d7.md,clients/T5/sessions/20261109T1855Z-T5-chat-obb-contract-b1d7.md
experiment_key=t5-obb-guid-unique-json-path-regression-v1:source-3aa107e:test-t5-obb-guid-contract:ubuntu-24.04:python3
resource_key=source-only-ci-t5-obb-contract
input_evidence=CI 42604230659 PNG unrelated SUCCESS; T5 scheduled path/JSON commits fd241958,6390967c,81b2813d tests unexecuted; no active Actions branch at 18:55 UTC.
next_step=Run source-only CI; inspect job steps; record result without claiming actual phone/OBB delivery verified.
status=active

## Executed and verified
- Scope registration commit: 5e9e058c49091f5f82d5481c861dd97f1d20b433; session initial commit a8364972238cf5d25194af81e7d20257c578a6ac.
- Added isolated source-only workflow in commit 0b2510460e6c54c519a6b494add5b0b0b103cda8; no shared game/test source changed.
- Actions https://github.com/alwansan/raf/actions/runs/42678868120 completed SUCCESS at 18:58:49Z; source checkout exact SHA 0b251046; job 129367641103.
- Verified raw CI job logs: python3 -m unittest -v scripts.test_t5_obb_guid_contract: Ran 10 tests, OK; python3 -m unittest discover -s tests -p 'test_t5_classify_obb_guid_logs.py' -v: Ran 16 tests, OK; py_compile passed. 26/26 total; independent regressions include spoofed root path, /sdcard alias, optional patch vs declared main, duplicate keys at nested JSON levels, invalid manifest.
- Other team jobs not canceled, no Unity/mini/full XAPK triggered. No REA needed for read-only Python manifest logic.

## Evidence limits and handoff
- CI verified classifier code behavior only using synthetic warning strings and logical manifest inventory; NOT actual OBB file contents, actual Android mounting, signed manifest identity or version pairing to installed phone APK.
- Device success of world/save/re-entry belongs to older artifact 42058825739 per docs/DEVICE_FEEDBACK_42058825739_AR.md; graphics unresolved. CL/test results not changed. Mini r4 remains NO_BUILD and game NOT_READY 0/3.
- Follow-up: retrieve actual signed delivery.json and same-run APK/OBB from downstream checkpoint for 42058825739 (not just parent staging artifacts); run classifier against pinned original LogRaft without printing private paths. Then distinguish current device cohort from old test. Do not rerun this exact CI without new inputs.
status=completed
