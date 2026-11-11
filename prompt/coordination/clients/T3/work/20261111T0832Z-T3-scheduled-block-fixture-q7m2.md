# T3 work 20261111T0832Z-T3-scheduled-block-fixture-q7m2
origin=scheduled
baseline_sha=791097cb7ee3c7dd33786452dcc1f87c90d8ad8b
scope= scripts/tests/test_t3_particle_material_chain_audit.py only
hypothesis= the regression test for block material lists passed literal backslash-n instead of a YAML line break, so it did not exercise the intended parser path.
experiment_key=T3-BLOCK-NEWLINE-FIXTURE-20261111
shared_resource=none; no CI dispatched; no game data touched.
result= changed fixture to actual newline, commit 9df92e422556a23e46c771d2904f78e25830af18.
verification= source inspection only; Python suite not executed in this runtime. Next: run python3 -m unittest scripts.tests.test_t3_particle_material_chain_audit and compare actual ZIP2/exported renderer chains.
