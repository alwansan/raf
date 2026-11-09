# T5 isolated work — 20261109T1750Z-T5-scheduled-obb-json-a9e4
origin=scheduled
baseline_sha=160187a334b8d672f1d1387c45c1d52301895c6f
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md
scope=scripts/t5_classify_obb_guid_logs.py, scripts/test_t5_obb_guid_contract.py
hypothesis=CLI delivery.json accepts duplicate keys through json.loads; metadata can silently be overridden, misattributing GUID warnings.
experiment_key=T5-OBB-JSON-UNIQUE-20261109
shared_resource=none; no Unity, APK, T4 mouse files
prior_session=clients/T5/sessions/20261109T1655Z-T5-scheduled-obb-path-f83c.md
plan=reject duplicate JSON keys at all nesting levels, regression-test malformed manifest, do not claim device verification.
