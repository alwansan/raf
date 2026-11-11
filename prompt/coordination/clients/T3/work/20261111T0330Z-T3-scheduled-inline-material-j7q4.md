# T3 scope — 20261111T0330Z-T3-scheduled-inline-material-j7q4
origin=scheduled
issue=RENDER-002 OPEN; NOT_READY 0/3
baseline_sha=66b532b0b73b62bcb14328121a8b420f51f89c6d
experiment_key=T3-PARTICLE-MATERIAL-INLINE-YAML-002
resource_key=none; source-only, no Unity/CI reservation
files=scripts/t3_particle_material_chain_audit.py; scripts/tests/test_t3_particle_material_chain_audit.py; prompt/coordination/clients/T3/sessions/20261111T0330Z-T3-scheduled-inline-material-j7q4.md
hypothesis=Unity YAML may encode m_Materials as inline [] or inline flow array; current audit only matches block lists and silently counts valid inline lists as absent. Test synthetic fixtures and fix only this diagnostic blind spot.
taken_over_from=20261111T0231Z-T3-scheduled-smoke-links-c9v2
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57
exclusions=T4 mouse, T5 resolution, T1/T2 water; no game assets, no APK, no CI duplicate.
