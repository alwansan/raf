# T3 scope — 20261111T2325Z-T3-scheduled-shader-ref-normalize-n4q8
origin: scheduled
issue_id: RENDER-002
base_sha: 9b29414952ddb1674b4a236abfe7df91a57761ba
status: completed_source_change_pending_test
intended_files:
- scripts/t3_material_dependency_pair_audit.py
- tests/test_t3_material_dependency_pair_audit.py
- prompt/coordination/clients/T3/sessions/20261111T2325Z-T3-scheduled-shader-ref-normalize-n4q8.md
experiment_key: T3-shader-ref-field-order-synthetic-9b294149
resource_key: none (CPU-only synthetic test)
hypothesis: m_Shader serialized mapping order is semantically irrelevant, but current comparison removes whitespace and compares raw order, creating false changed_shader_reference_materials.
nonoverlap: T3 pair audit only; GT 82-owner proof, T1/T2 water, T4 input, T5 resolution/build untouched.
next: canonicalize shader fileID/guid/type and add a regression, verify on synthetic test. No original asset export or phone claim.

result_commits: 874f4cd1c3d9bb409969e3504dce8a483cd5fbe4, 80e089833e9d4e6ddc3a9dd2a9ed6dafbebbf102
session_commit: 4b8827d3400aa34707507aa7821ab6f82237ed4b
validation: Python tests not executed; no CI launched; source-only change
