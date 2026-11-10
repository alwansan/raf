# T3 scope 20261110T0527Z-T3-scheduled-render-state-diff-p7q4
origin: scheduled
baseline_sha: c7d626fdcb9345615f66c16f07a73080c1e2d923
issue: RENDER-002
experiment_key: t3-render-state-pair-diff-v1
files: scripts/t3_render_state_pair_diff.py; tests/test_t3_render_state_pair_diff.py; this scope; independent T3 session
shared_resource: none; no Unity/CI/ZIP2 download
hypothesis: explicit normalized original/export state mismatch can be classified without disclosing raw material names.
boundary: summary comparison ONLY; no authenticity, material matching, source shader extraction, pixel fix or Android claim.
taken_over_from: T3 20261110T0426Z provenance coverage and prior original smoke34 pass-state probe.
observations: 5 Nov device report shows square smoke/white raft; 8 Nov report confirms fire/lighting remain missing. Existing 14 tests are structural only.
next: authenticate source/export pair from same shader pass and shader owner; feed private normalized state into comparator, then compare alpha/particle texture evidence.
