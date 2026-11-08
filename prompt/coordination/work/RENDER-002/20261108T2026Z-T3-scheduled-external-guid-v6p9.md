# T3 scoped work 20261108T2026Z-T3-scheduled-external-guid-v6p9
origin: scheduled
issue_id: RENDER-002
status: active
baseline: 9b89f62772c2c61f6269fd2249f8560af1522892 (recent repository commit search; branch HEAD not independently established)
resumed_from: 20261108T1930Z-T3-scheduled-crlf-renderer-b7q2
intended_files: scripts/t3_particle_external_material_resolution.py; tests/test_t3_particle_external_material_resolution.py; clients/T3/sessions/20261108T2026Z-T3-scheduled-external-guid-v6p9.md
experiment_key: external-particle-material-guid-meta-presence-v1-source-yaml
resource_key: none (read-only local Python, no Unity)
hypothesis: external ParticleSystemRenderer Material GUIDs can be triaged against .mat.meta owners without exposing asset identities; missing vs duplicate vs unique metadata owner are distinct, and no match does not prove loss when export scope is partial.
No game resource edits, no Actions dispatch, no raw assets, no device claim. T4 mouse and T5 resolution excluded.
