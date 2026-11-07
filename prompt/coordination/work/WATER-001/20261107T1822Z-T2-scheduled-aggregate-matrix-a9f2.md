# T2 WATER-001 isolated aggregate permutation validation
session_id: 20261107T1822Z-T2-scheduled-aggregate-matrix-a9f2
origin: scheduled
baseline_sha: 19c0f6bf077936522487355343c9438fceaf0ecc
issue: WATER-001
experiment_key: T2-FOAM-AGGREGATE-81-SOURCEFREE-V1
files: tests/test_t2_foam_pass_aggregate_matrix.py (new); this work record; independent session
hypothesis: aggregate checker must preserve pass0/pass1 source/destination for all 81 valid source-free combinations and reject single-field total corruption.
shared_resource: none; no native CI, original assets, ShaderLab or T3 files.
taken_over_from: previous T2 scheduled aggregate checker commit 69072c3b and chat direct producer CI 42305522855.
owner_device: 42058825739 confirms world entry/save/reentry from artifact, NOT restored water.
verification: source inspection; CI/local original repository tests not executed in this run.
next: run python -m unittest tests.test_t2_foam_pass_aggregate_matrix from authentic checkout; then integrate sanitized per-pass producer evidence from original Mono.Cecil.
