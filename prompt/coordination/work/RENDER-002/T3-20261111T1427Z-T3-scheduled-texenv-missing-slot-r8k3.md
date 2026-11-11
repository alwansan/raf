# T3 scope 20261111T1427Z-T3-scheduled-texenv-missing-slot-r8k3
origin=scheduled
issue_id=RENDER-002
base_sha=ff1ca145ae0cf45c62a38ad918ec33a58c3d2e30
status=active
intended_files=scripts/t3_material_texture_binding_audit.py;tests/test_t3_material_texture_binding_audit.py;prompt/coordination/clients/T3/sessions/20261111T1427Z-T3-scheduled-texenv-missing-slot-r8k3.md;this work file
experiment_key=T3-TEXENV-UNBOUND-SLOT-COUNT-v1-20261111
resource_key=none; source-only; no Unity/CI/ZIP2
hypothesis=TexEnv scanner silently drops a missing m_Texture line when followed by another slot; undercounts malformed export and can conceal missing binding. Preserve safe aggregate output and all original GUID/meta.
resumed_from=20261111T1331Z-T3-scheduled-texref-h6m4; original same-export 41939404454; owner device report 42058825739.
Coordination: T4 pointer/T5 display untouched; no duplicate workflow.
updated_at=2026-11-11T14:27:00Z
