# T3 RENDER-002 scoped plan
session_id=20261110T2030Z-T3-scheduled-guid-multiline-k4v9
origin=scheduled
baseline_head=8550bfdf7d453b57e74c14cb268afe02e11ae35d
scope=read-only Unity YAML GUID audit only; scripts/t3_unity_guid_link_audit.py, tests/test_t3_guid_audit_regression.py, this work and independent session.
hypothesis=YAML object references can span lines, while current REF_BLOCK accepts newlines but REF_FILE_ID/REF_GUID token anchoring must be checked with exact synthetic fixtures; prioritize demonstrated false-negative only.
experiment_key=T3-GUID-MULTILINE-20261110; shared_resource=none; no Unity/native/ZIP2/CL writes.
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 world save/reentry confirmed, visual defects open.
prior=20261110T1931Z-T3-scheduled-guid-regex-proof-q5m8; source commit 993f36ad.
Do not modify T4 mouse, T5 display, T1/T2 water. Verify current branch before any subsequent source mutation; do not force.
