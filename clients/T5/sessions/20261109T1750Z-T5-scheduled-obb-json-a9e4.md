# T5 scheduled engineering checkpoint
session_id=20261109T1750Z-T5-scheduled-obb-json-a9e4
origin=scheduled
baseline_sha=160187a334b8d672f1d1387c45c1d52301895c6f
scope_commit=35e871038210bd0882557c85e09c62803653729e
source_commit=6390967ca26da6a60cc1ea1c271a065402398b20
test_commit=81b2813da4ac1ad397b0d40015bc3d68532daedd
observed_head_before_session=81b2813da4ac1ad397b0d40015bc3d68532daedd
work=work/T5/20261109T1750Z-T5-scheduled-obb-json-a9e4.md
resumed_from=clients/T5/sessions/20261109T1655Z-T5-scheduled-obb-path-f83c.md

## Evidence and result
Read owner feedback, team guidance, prior T5 sessions, latest HEAD and recent Actions. Existing LogRaft OBB GUID classifier used default json.loads in CLI, allowing duplicate delivery metadata keys to silently override earlier fields. Added load_delivery_json with object_pairs_hook duplicate rejection at every nesting level and two regression methods for duplicate root/nested fields and valid JSON. Source and test commits are published; no game assets modified.

## Proof boundary
Tests not executed in Python/CI this cycle because runtime checkout unavailable; source review only. No signed APK/OBB bytes or exact device delivery.json available for pairing, no device screenshots/Resolution test or controlled performance cohort measured. Owner's world/save/reentry remains limited to Artifact 42058825739. Right-hand three buttons still need device verification; mouse T4 scope not touched. Mini lab r4 NO_BUILD, full game NOT_READY.

## Next
Run python -m unittest scripts.test_t5_obb_guid_contract in full checkout; investigate any failure. Feed only the exact signed delivery.json and raw LogRaft log into classifier; separately follow Settings Resolution original binding and 3-button safe-area proof. Do not repeat Unity or claim phone PASS.
