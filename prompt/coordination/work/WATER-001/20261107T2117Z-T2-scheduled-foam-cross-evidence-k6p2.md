# T2 WATER-001 — original aggregate / per-pass role consistency gate
session_id: 20261107T2117Z-T2-scheduled-foam-cross-evidence-k6p2
origin: scheduled
baseline_sha: 3b32b338c0783a1def74151b60cc36cb59e1f1dc
experiment_key: T2-FOAM-ORIGINAL-AGGREGATE-ROLE-CROSSCHECK-V1
scope: scripts/t2_foam_pass_crosscheck.py (new), tests/test_t2_foam_pass_crosscheck.py (new), this work and independent session
hypothesis: two independently sanitized Foam per-pass reports can silently disagree despite each passing its own schema; a fail-closed join must reject mismatch and only emit safe classifications.
taken_over_from: T2 role gate da7ac14e; aggregate checker 69072c3b; matrix 3fe16a90; original IL source CI 42308583977.
owner_device: 42058825739 confirms world/save/reentry but not restored water; original 220911 log 23884 water pass and 3850 FFT errors.
shared_resource: none. No Unity, ZIP2 raw data, game shader, T3 file, CI build or workflow.
plan: validate original aggregate via existing original validator and check_counts, validate role schema and duplicate JSON keys, compare pass0/pass1 exactly; add source-free mismatch tests. Do not infer actual render or source pass1 producers.
coordination: independent scripts/tests only, no overlapping existing files.
status: scoped; next publish source/test and run local isolated tests if executable checkout possible.
