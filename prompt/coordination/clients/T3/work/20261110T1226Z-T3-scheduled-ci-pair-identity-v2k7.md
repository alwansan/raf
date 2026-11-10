# T3 work — 20261110T1226Z-T3-scheduled-ci-pair-identity-v2k7
origin: scheduled
issue_id: RENDER-002
base_sha: c03c24a94b282d673d1fc63fb2077658692dc579
status: active
intended_files: scripts/t3_render_state_pair_identity.py; scripts/tests/test_t3_render_state_pair_identity.py; this work file; clients/T3/sessions/20261110T1226Z-T3-scheduled-ci-pair-identity-v2k7.md
experiment_key: render-state-pair-identity-v1|source=authenticated-private-summary|input=sha256+material+shader+pass|runner=python-stdlib
resource_key: none (CPU only)
hypothesis: current comparator can compare two structurally valid summaries from different materials/shader passes, reporting misleading MATCH; gate identity and independent SHA-256 before comparison.
last evidence: CI 42799750403 SUCCESS on ef457271 (three regression tests); phone artifact 42058825739 world save/reentry yes, rendering unresolved.
constraints: no original asset publication; do not change game assets, .meta, shaders, touch, Settings or shared workflow; no CI duplicate.
next: implement and locally test strict same-identity provenance envelope validator, keeping unknown source provenance as unproven.
