# T3 scoped work — 20261111T0633Z-T3-scheduled-block-sequence-w7m2
origin=scheduled
baseline_head=5fcddeb967dd2120b27eb0762af5f277c5819441
issue=RENDER-002
experiment_key=T3-PARTICLE-BLOCK-SEQUENCE-SAME-INDENT-001
scope=scripts/t3_particle_material_chain_audit.py; scripts/tests/test_t3_particle_material_chain_audit.py; own session file
hypothesis=Unity YAML block sequence item at same indentation as m_Materials field is valid, but parser rejects it due <= comparison, causing false empty material list; sibling lists must remain excluded.
shared_resource=none; no Unity build or Actions dispatch
prior_evidence=20261111T0533Z-T3-scheduled-block-indent-n4q8; DEVICE_FEEDBACK_42058825739_AR.md
verification=source-level regression and isolated synthetic test; no ZIP2, phone, shaders or textures claimed.
next=fix one indentation boundary and add explicit positive/negative tests, preserve other team scopes.
