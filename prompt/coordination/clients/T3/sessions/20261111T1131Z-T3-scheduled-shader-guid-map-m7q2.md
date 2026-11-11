# T3 scheduled checkpoint — 20261111T1131Z-T3-scheduled-shader-guid-map-m7q2
origin: scheduled
issue_id: RENDER-002
resumed_from_sessions: 20261111T1026Z-T3-scheduled-multirenderer-audit-v5k9; 20261108T2013Z-T3-chat-cl-pixelcopy-surface-f2n8
base_evidence: DEVICE_FEEDBACK_42058825739_AR.md; 41939404454; 41940350604
scope: prompt/coordination/work/RENDER-002/20261111T1131Z-T3-scheduled-shader-guid-map-m7q2.md
result: Added static read-only Unity .mat m_Shader -> .meta GUID owner census, distinguishing unique, missing-in-supplied-tree, duplicate, builtin/local, null and missing. It does not print raw paths or GUIDs.
code_commit: b71e908e3b3206b4a5acd11639c9050e737da8c4
test_commit: d63576ccab7f189aafd436e0f5d04f4ec8140c1f
local_test: 2/2 PASS on equivalent local implementation and fixtures (Python unittest); repository CI has not executed these new tests.
owner_device: 42058825739 world/save/re-entry PASS on phone; white materials, lighting and square smoke OPEN. Water FFT log errors are distinct. No new phone test or XAPK.
limitations: No authenticated ZIP2 vs actual exported material/shader chain tested; no claim that GUID failure causes white or square smoke. .mat only; ShaderGraph/package references and imported variants not proven. The source/export parity already proved 41 materials' 227 UV and 150 RGBA slots and rules those losses out for that bounded set.
next: Run scripts/tests/test_t3_material_shader_binding_audit.py in source CI or authenticated ZIP2/actual-export material tree; compare source/export GUID owner counts and inspect any mismatch privately, then follow smoke ParticleRenderer->Material->Shader->Texture. Coordinate T1/T2 water and T4/T5 separate scopes. Do not duplicate heavy Actions.
status: SOURCE_TOOL_TESTED_LOCAL_ONLY; RENDER-002 OPEN; NOT_READY 0/3
