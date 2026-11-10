# T3 scoped work 20261110T2133Z-T3-scheduled-guid-coverage-h6p2
origin=scheduled
issue_id=RENDER-002
status=active
baseline_reference=20261110T2030Z-T3-scheduled-guid-multiline-k4v9
intended_files=scripts/t3_unity_guid_link_audit.py;tests/test_t3_guid_audit_regression.py;prompt/coordination/clients/T3/sessions/20261110T2133Z-T3-scheduled-guid-coverage-h6p2.md
experiment_key=unity-guid-audit-skipped-oversize-v1:MAX_BYTES-33554432:static-YAML
resource_key=none
hypothesis=The existing auditor silently omits oversized Unity YAML and .meta files, potentially producing misleading zero unresolved GUID references; expose skipped-file counts and a coverage-incomplete flag without changing game resources.
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md
prior_evidence=993f36ada1b38bcf4b9379c50faeb9de197f22a0;a2b73efb5836a4627ea63205c5b74362ab9d7c1b
scope_boundary=No game assets, original data, Unity build, shared workflows, mouse, resolution or audio. Source-only audit reliability.
