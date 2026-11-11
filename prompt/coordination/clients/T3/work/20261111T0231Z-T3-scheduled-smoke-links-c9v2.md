# T3 work scope — 20261111T0231Z-T3-scheduled-smoke-links-c9v2
origin=scheduled
issue_id=RENDER-002
status=active
base_sha=ef8a01ff22bdc237ac1b885f59b3d1abf0b1f912
intended_files=scripts/t3_particle_material_chain_audit.py; prompt/coordination/clients/T3/sessions/20261111T0231Z-T3-scheduled-smoke-links-c9v2.md
experiment_key=T3-PARTICLE-MATERIAL-LINK-STATIC-001:UnityYAML:particle-renderer-to-material:hash-only
resource_key=none (read-only caller-provided tree)
hypothesis=Square smoke could be a particle renderer using missing material, incorrect shader binding, or alpha/blend; static YAML can prove renderer-to-material references but cannot prove GPU behavior.
Owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Artifact 42058825739 world/save/reenter success; RENDER-002 open.
No shared game source edits, no CI, no APK. T4 mouse and T5 resolution excluded.
