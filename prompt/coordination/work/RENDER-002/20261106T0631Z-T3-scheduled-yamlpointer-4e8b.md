# T3 scope 20261106T0631Z-T3-scheduled-yamlpointer-4e8b
origin: scheduled
issue_id: RENDER-002
baseline_sha: 3d95465485f47f61d24ea1cbf8e89f4389e72b30
resumed_from_session: 20261106T0527Z-T3-scheduled-identity-6e29
intended_files: scripts/t3_shader_identity_gate.py; scripts/tests/test_t3_shader_identity_gate.py (if present); this work file; own session
experiment_key: t3-yaml-material-pointer-comment-and-fileid-20261106
resource_key: none (source-only; no Unity)
hypothesis: unanchored m_Shader regex can accept a commented fake pointer and reject genuine alternate YAML spacing; fail closed for comments and accept legitimate YAML formatting.
status: active
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57
No other T work files modified; no heavy CI planned.
