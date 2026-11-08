# T3 RENDER-002 isolated audit boundary
session_id: 20261108T0526Z-T3-scheduled-symlink-boundary-n6r2
origin: scheduled
issue_id: RENDER-002
status: completed_source_unverified
updated_at: 2026-11-08T05:26:00Z
intended_files: scripts/t3_material_shader_link_audit.py; tests/test_t3_material_shader_link_audit.py; own session and event
experiment_key: t3-material-shader-audit-symlink-input-boundary-v1
resource_key: none (CPU-only synthetic fixtures)
Hypothesis: a .mat or .shader.meta symlink can cause the read-only audit to inspect files outside the supplied scan tree; this violates its stated scan boundary and makes aggregate counts misleading. Reject symlink inputs without touching real Unity assets.
Baseline: prior T3 session 20261108T0427Z-T3-scheduled-duplicate-shader-guid-q8m4.md; shader GUID ambiguity protection already present. Owner device report 42058825739 read. No Unity/APK requested.

Outcome: source commit 1d9e16904dcc1e6b6b7c334597d151f5df6f59e3; test fixture correction 017190599cd21e2108e3fb315c36963a22689303. Test execution pending; session and event recorded. No shared resources held.
