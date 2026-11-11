# T3 independent scope
session_id: 20261111T1131Z-T3-scheduled-shader-guid-map-m7q2
origin: scheduled
issue_id: RENDER-002
status: active
experiment_key: t3-material-shader-guid-map-static-v1-unity-yaml-meta
resource_key: none (source-only)
intended_files: scripts/t3_material_shader_binding_audit.py; scripts/tests/test_t3_material_shader_binding_audit.py; prompt/coordination/clients/T3/sessions/20261111T1131Z-T3-scheduled-shader-guid-map-m7q2.md
hypothesis: Some white materials may point to absent or ambiguous Shader GUID owners; distinguish missing, duplicate, unique and built-in references before blaming texture UV or tint.
Evidence: 41939404454 proved 227/227 UV and 89/89 internal texture matches; 41940350604 proved 150/150 RGBA source/export slots in 41 selected materials. This does not validate Shader bindings.
Scope: read-only static parser with synthetic tests; no Unity, game assets, XAPK, shared lab, T4 mouse or T5 display files. Avoid publishing raw paths or GUIDs.
