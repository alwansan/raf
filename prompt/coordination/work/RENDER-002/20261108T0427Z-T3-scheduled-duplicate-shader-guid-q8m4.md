# T3 RENDER-002 scope
session_id: 20261108T0427Z-T3-scheduled-duplicate-shader-guid-q8m4
origin: scheduled
issue_id: RENDER-002
status: active
base_sha: fedd51d3e2b07af1b987eb659f8d8290f80da3ca
resumed_from_session: 20261108T0326Z-T3-scheduled-fixture-6b2d
intended_files: scripts/t3_material_shader_link_audit.py; tests/test_t3_material_shader_link_audit.py; this work; clients/T3/sessions/20261108T0427Z-T3-scheduled-duplicate-shader-guid-q8m4.md
experiment_key: material-shader-guid-duplicate-fail-closed-v1-source-audit
resource_key: none (no Unity/CI)
hypothesis: duplicate GUIDs among physically present .shader.meta files can be incorrectly counted as resolved; classification must distinguish ambiguous GUID from uniquely resolved GUID.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57
owner_device_acceptance: world/save/reload only on artifact 42058825739; white surfaces, lighting and square smoke unresolved.
exclusions: no game resources, shaders, .meta, audio, settings, mouse, buttons, Resolution, native workflow or build request.
