# T5 OBB GUID warning classification regression
session_id=20261109T1552Z-T5-scheduled-obb-guid-regression-c4e9
origin=scheduled
baseline_sha=599abc10061aaa5ec2fbdb3853602bcd1f657f44
experiment_key=T5-OBB-GUID-REGRESSION-20261109
scope=scripts/test_t5_obb_guid_contract.py only; no Unity, Settings, T4 mouse, shared testpack, or native build.
hypothesis=An optional patch GUID lookup must never be reported as a corrupt main OBB, and version mismatch must be segregated.
inputs=synthetic warning strings; source scripts/t5_classify_obb_guid_logs.py
evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; original device reports one/two GUID warnings but exact signed delivery manifest remains unverified.
shared_resource=none
execution=Python syntax compiled locally; full unittest against repository module awaits CI/local checkout.
next=run python3 -m unittest scripts.test_t5_obb_guid_contract after fetching branch; use actual signed delivery.json plus LogRaft logs for device classification.
