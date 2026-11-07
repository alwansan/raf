# T3 session 20261107T1233Z-T3-scheduled-drift-ci-audit-m6q2
origin=scheduled
issue_id=RENDER-002
status=SOURCE_TEST_ADDED_PENDING_CI
resumed_from_sessions=20261107T1126Z-T3-scheduled-drift-coverage-k4p8;20261107T1035Z-T3-scheduled-private-pair-contract-c4e7
baseline_sha=6946cd348d15a70131c21f24e0ed6838fdbc18b7
scope_commit=71e258530739f0f59c774daf839d3ab2236a6020
test_commit=b884e21269fe95e78cad438da86c08c5e6d20895
origin_run=scheduled

## Evidence and change
Read owner phone feedback 42058825739 and CL screenshot/log references; world entry/save/reentry was reported successful on the earlier artifact, while white hand/raft, lighting and square smoke remain unresolved. Read live AGENTS/owner requirements/T_TEAM protocols and trial vote ledger. Existing RGB export 41968665857 reported 106 matched pairs, 30 RGB drift and 76 exact; aggregate JSON lacks individual format/sRGB metadata. Prior T3 guard adds --require-drift-metadata but was pending CI. Added an independent regression in tests/test_t3_rgb_drift_strata.py: 105/106 format values are known and all 76 exact are known, yet one RGB-drift pair has unknown format. The weaker --require-metadata passes; --require-drift-metadata must reject. This tests a missing-format case distinct from prior sRGB tests.

## Boundaries and next step
No game assets, shader, prefab, .meta, GUID, .rgd, mouse, Settings or native workflow modified. No Unity job dispatched; no proof of on-device pixel repair. New test is source-published but NOT YET RUN on CI. Execute PYTHONPATH=scripts python3 -m unittest discover -s tests -p test_t3_rgb_drift_strata.py, then extract per-pair private original format/sRGB metadata to classify 30 RGB drift textures, map relevant material/particle shader links, and compare with CL screenshots. Do not publish original asset bytes or filenames. Trial vote remains 'لا يحتاج' absent integrated device-facing fix. RENDER-002 OPEN / NOT_READY.
