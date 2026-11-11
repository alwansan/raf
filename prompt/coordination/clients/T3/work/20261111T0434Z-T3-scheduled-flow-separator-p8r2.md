# T3 work 20261111T0434Z-T3-scheduled-flow-separator-p8r2
origin=scheduled
baseline_sha=1d4040b08d40520bd678ac5f5af98fcc1509887d
issue=RENDER-002 OPEN
experiment_key=T3-PARTICLE-FLOW-SEPARATOR-003
scope=scripts/t3_particle_material_chain_audit.py; scripts/tests/test_t3_particle_material_chain_audit.py; own work/session files
hypothesis=The flow-style parser accepts malformed adjacent map entries without a comma and can misclassify corrupt material YAML as verified bindings. Preserve fail-closed classification and add regression.
shared_resource=none; no Unity CI, no APK build
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md and CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57
resumed_from=20261111T0330Z-T3-scheduled-inline-material-j7q4
limitations=synthetic structural test only; not original ZIP2/export or device proof
