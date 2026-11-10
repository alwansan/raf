# T3 work — 20261110T1226Z-T3-scheduled-ci-pair-identity-v2k7
origin: scheduled
issue_id: RENDER-002
base_sha: c03c24a94b282d673d1fc63fb2077658692dc579
status: completed
intended_files: scripts/t3_render_state_pair_identity.py; scripts/tests/test_t3_render_state_pair_identity.py; this work file; clients/T3/sessions/20261110T1226Z-T3-scheduled-ci-pair-identity-v2k7.md
experiment_key: render-state-pair-identity-v1|source=authenticated-private-summary|input=sha256+material+shader+pass|runner=python-stdlib
resource_key: none (CPU only)
hypothesis: current comparator can compare two structurally valid summaries from different materials/shader passes, reporting misleading MATCH; gate identity and independent SHA-256 before comparison.
last evidence: CI 42799750403 SUCCESS on ef457271 (three regression tests); phone artifact 42058825739 world save/reentry yes, rendering unresolved.
constraints: no original asset publication; do not change game assets, .meta, shaders, touch, Settings or shared workflow; no CI duplicate.
result: Added scripts/t3_render_state_pair_identity.py and scripts/test_t3_render_state_pair_identity.py; local 8/8 checks passed against interface-compatible comparator copy; repository 9th shader identity test added after local run, not CI-verified. Source SHA field is syntax-validated only; no source bytes authenticated. CI 42799750403 success at ef457271 confirms prior type-parity regressions, not this gate.
commits: 30cbf7e10d9178ccd7b3fa6d59b7bede26ac8dd3; e1bfd7750635aed3e1e3064547464b7ce3d5d4c5
next: run 9/9 on checked-out repo and feed two authenticated original/export records from same material/pass; do not claim graphics fix.
