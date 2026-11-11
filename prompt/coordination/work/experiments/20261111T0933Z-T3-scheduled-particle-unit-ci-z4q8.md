# T3 source-only particle material YAML audit
session_id=20261111T0933Z-T3-scheduled-particle-unit-ci-z4q8
experiment_key=T3-particle-yaml-parser-unit-python311-20261111-source-494829d
source_sha=074759c37eca8a56d754deee9bcd5660aa4e2bbc
command=python3 -m unittest discover -s scripts/tests -p 'test_t3_particle_material_chain_audit.py' -v
scope=11 synthetic parser regressions, no ZIP2, no game raw assets, no device
status=waiting_ci
workflow=.github/workflows/raft-t3-particle-material-audit-unit.yml
expected=all tests pass and py_compile; failure requires narrow fix
limitations=No original material/export parity and no phone rendering proof.
