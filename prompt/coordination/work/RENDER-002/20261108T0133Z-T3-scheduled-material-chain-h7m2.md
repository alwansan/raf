# 20261108T0133Z-T3-scheduled-material-chain-h7m2
origin: scheduled
issue_id: RENDER-002
status: completed_source_only
base_sha: 614c81662f08294638fce1d471a1823f132e5677
updated_at: 2026-11-08T01:33:00Z
resumed_from_session: 20261108T0029Z-T3-scheduled-first-session-a7c3
intended_files: scripts/t3_material_shader_link_audit.py; tests/test_t3_material_shader_link_audit.py; this work file; clients/T3/sessions/20261108T0133Z-T3-scheduled-material-chain-h7m2.md
experiment_key: material-yaml-shader-pptr-aggregate-audit-v1
resource_key: none (source-only Python)
Hypothesis: distinguish missing/dangling Material m_Shader PPtr references from resolved links, without printing private paths. Synthetic regression and no GPU claims. T4 mouse and T5 resolution remain separate.

## Result
Integrated source-only aggregate Material -> Shader GUID audit at deee68b9, corrected regex escaping at 6d19fb4e, and added synthetic regression tests at e9995210. Two standalone regex probes passed locally; committed unittest suite was not executed because the local checkout is unavailable (GitHub DNS resolution failure). This audit is for Unity text .mat/.shader.meta only and cannot inspect serialized binary materials, shader variants, blend state, device rendering or the CL screenshot pixels. An unresolved GUID means only absent from the scan tree, not missing from the full project. No Unity or game assets modified.
Next: run python -m unittest tests.test_t3_material_shader_link_audit on checked-out HEAD; run audit against full verified exported Assets and Packages tree, compare aggregate unresolved counts and trace targeted renderer materials privately; inspect CL screenshot pixels and correlate with shaders before any render fix.
