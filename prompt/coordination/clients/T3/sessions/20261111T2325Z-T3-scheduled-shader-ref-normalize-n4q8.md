# T3 checkpoint — 20261111T2325Z-T3-scheduled-shader-ref-normalize-n4q8
origin: scheduled
issue_id: RENDER-002
resumed_from_sessions:
- 20261111T2238Z-T3-scheduled-fileid-k7m4
base_sha: 9b29414952ddb1674b4a236abfe7df91a57761ba
scope_commit: 7961f0635cbc16b5923c013cfab2ec6dc1329478
code_commit: 874f4cd1c3d9bb409969e3504dce8a483cd5fbe4
test_commit: 80e089833e9d4e6ddc3a9dd2a9ed6dafbebbf102
origin_device_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; successful save/reentry only; graphics unresolved.
recent_independent_evidence: GT workflow 43118214676 success on 3fd0bdb, validates 82-owner material target identity structurally, not Android appearance.
result: Corrected a source-level false-positive: m_Shader PPtr identity now compares canonical fileID/guid/type rather than serialized field order. Added two synthetic regression cases (reordered equivalent pointer; changed fileID).
validation: NOT EXECUTED. GitHub writes verified; Python tests not run on this candidate, original ZIP2/export pair not compared, no Unity/phone validation.
files:
- scripts/t3_material_dependency_pair_audit.py
- tests/test_t3_material_dependency_pair_audit.py
no_overlap: GT 82-owner proof and T1/T2/T4/T5 scopes unchanged. No CI dispatched.
next: run python -m unittest tests.test_t3_material_dependency_pair_audit and investigate any failures; then compare verified original/export trees with same path matching. Follow GT 82-owner material graph to map white hand/raft/square particle to specific shaders and keywords, rather than treating a static ref change as visual proof.
