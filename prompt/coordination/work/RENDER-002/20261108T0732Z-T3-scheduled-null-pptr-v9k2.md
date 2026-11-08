# T3 scoped work
session_id: 20261108T0732Z-T3-scheduled-null-pptr-v9k2
origin: scheduled
issue_id: RENDER-002
status: active
updated_at: 2026-11-08T07:32:00Z
intended_files: scripts/t3_material_shader_link_audit.py; tests/test_t3_material_shader_link_audit.py; this work file; clients/T3/sessions/20261108T0732Z-T3-scheduled-null-pptr-v9k2.md
experiment_key: t3-unity-material-shader-pptr-zero-fileid-nonzero-guid-fail-closed-source-fixture-v1
resource_key: none (source-only)
hypothesis: A zero fileID with nonzero GUID is a null PPtr, but the audit currently reports it as a resolved shader if that GUID exists. This is a false-positive restoration claim.
base_observed: material audit source blob from GitHub at 2026-11-08; prior T3 session 20261108T0630Z-T3-scheduled-parser-boundary-f4c9.
owner_phone: 42058825739 world/save/reopen success only; white hand/raft and square smoke remain open. No Unity/CI dispatch or raw assets.
coordination: T3-only source audit/test, no T1/T2 water, T4 mouse, T5 resolution/packaging files.
next: add regression, fix classifier, run local source tests, publish independent session evidence.
