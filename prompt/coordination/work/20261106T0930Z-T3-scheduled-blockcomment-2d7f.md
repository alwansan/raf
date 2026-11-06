# T3 scope — Shader48 block-comment false positive
session_id: 20261106T0930Z-T3-scheduled-blockcomment-2d7f
origin: scheduled
baseline_sha: 991a51b7fc26eeaabd083386be51d3b99bfecf96
issue: RENDER-002
hypothesis: the current ^\\s*Shader declaration regex treats a Shader token inside a multiline /* ... */ comment as a genuine ShaderLab declaration; structural gate false positive.
files: scripts/t3_shader_identity_gate.py; scripts/test_t3_shader_identity_gate_syntax.py; own work and session files.
experiment_key: T3-SHADER48-BLOCKCOMMENT-20261106-2d7f
shared_resource: none; no CI/Unity build.
taken_over_from: T3 20261106T0825Z-T3-scheduled-empty-shader-gate-7c2a; B_TEAM historical rendering evidence.
expected_sha_policy: re-read live HEAD and source blob SHA before update, never force.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (world/save/reentry confirmed only for artifact 42058825739).
status: scoped
