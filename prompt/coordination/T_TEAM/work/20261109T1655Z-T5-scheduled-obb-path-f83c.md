# T5 independent scope
session_id=20261109T1655Z-T5-scheduled-obb-path-f83c
origin=scheduled
base_sha=6611d62b7b1df6c3fcd576fead03e2b1ee713f25
issue_id=OBB-GUID-PATH-ATTRIBUTION
status=active
intended_files=scripts/t5_classify_obb_guid_logs.py,scripts/test_t5_obb_guid_contract.py,clients/T5/sessions/20261109T1655Z-T5-scheduled-obb-path-f83c.md
experiment_key=obb-guid-strict-android-obb-root-v1:source-6611d62:synthetic-paths
resource_key=none
hypothesis=Current regex accepts /tmp/Android/obb/<package>/main... as actual Android OBB path, leading to misleading warning attribution.
owner_notes=Do not modify T4 pointer input, T1/T2 water or shared Unity. No CI dispatch. Signed APK/OBB and device proof remain outstanding.
