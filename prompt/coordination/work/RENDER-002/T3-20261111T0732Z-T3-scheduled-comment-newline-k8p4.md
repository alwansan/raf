# T3 scoped work — 20261111T0732Z-T3-scheduled-comment-newline-k8p4
origin=scheduled
base_sha=607a4b77c9b7252cdfd5ceffa41a27b5859bc2c0
issue_id=RENDER-002
status=active
intended_files=scripts/t3_particle_material_chain_audit.py; scripts/tests/test_t3_particle_material_chain_audit.py; prompt/coordination/clients/T3/sessions/20261111T0732Z-T3-scheduled-comment-newline-k8p4.md
experiment_key=T3-PARTICLE-ESCAPED-COMMENT-NEWLINE-SYNTAX-001
resource_key=none
hypothesis=Literal escaped newline sequences inside a Python comment swallowed material_indent assignment and tail initialization; parser fails at runtime with UnboundLocalError for block lists.
resumed_from=20261111T0633Z-T3-scheduled-block-sequence-w7m2
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md
validation=compile and synthetic unittest via isolated source copy; no raw game data, no CI build.
