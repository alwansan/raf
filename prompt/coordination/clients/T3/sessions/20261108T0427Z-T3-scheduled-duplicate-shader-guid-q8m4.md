# T3 session 20261108T0427Z-T3-scheduled-duplicate-shader-guid-q8m4
origin: scheduled
issue_id: RENDER-002
resumed_from_session: 20261108T0326Z-T3-scheduled-fixture-6b2d
baseline_sha: fedd51d3e2b07af1b987eb659f8d8290f80da3ca
work_scope_commit: e80ffca7fbaf90ee836e21f48a62b0aa738118fb
source_commit: 5a4b0cb2b7bc69d2d6320f7abb4a8e3a5330e794
test_commit: b1e4d35539ed0bea19c056fcefba31e9724f1bc8
origin_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57
result: Material->Shader audit now counts duplicate GUIDs among present shader sources and classifies matching Material references as ambiguous, not resolved. Added synthetic duplicate fixture and corrected escaped newlines.
validation: Source reviewed after publication; full unittest not executed because local GitHub DNS resolution failed (git ls-remote: Could not resolve host github.com). No Unity/device/ZIP2 original execution, no pixel proof.
actions: Recent T1 diagnostic run 42445720118 completed success, not duplicated. No native build launched.
device: owner confirmed world/save/exit/re-entry on artifact 42058825739; white hand/raft, lighting and square smoke remain open.
limitations: duplicated GUID is a possible audit false-positive, not demonstrated cause of device whiteness. No source assets or .meta changed.
next_step: run python -m unittest tests.test_t3_material_shader_link_audit on fetched branch; audit authenticated same-instance export tree, then trace actual white material and smoke ParticleSystemRenderer to shader/texture/alpha states. Preserve RENDER-002 OPEN / NOT_READY.
