# 20261108T0326Z-T3-scheduled-fixture-6b2d
origin: scheduled
issue_id: RENDER-002
status: active
intended_files: tests/test_t3_material_shader_link_audit.py; prompt/coordination/work/RENDER-002/20261108T0326Z-T3-scheduled-fixture-6b2d.md; prompt/coordination/clients/T3/sessions/20261108T0326Z-T3-scheduled-fixture-6b2d.md
experiment_key: material-shader-meta-source-fixture-regression-v1-source-0c410ac8-test-31e22967
resource_key: none (synthetic local unit test)
base: source blob 0c410ac84f19ce7a0074db275e8902b5a5a7422d; test blob 31e229672bc576137ccec7c64fb6785ab4a2d3e7
hypothesis: Prior T3 shader-meta orphan guard requires an actual .shader source, but its existing resolved fixture writes only .shader.meta, causing the previously published unit test to fail. Repair fixture and add an orphan negative test without touching game assets or other teams' files.
owner: T3
updated_at: 2026-11-08T03:26:00Z
No Unity, APK, original asset, or CL modification. Phone result 42058825739 remains owner-confirmed only. Next: test locally, publish test with blob-SHA guard, write independent session.
