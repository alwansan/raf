# T5 independent scope — resolution delegate evidence gate
session_id: 20261111T1748Z-T5-scheduled-resolution-graph-m6q8
origin: scheduled
baseline_head: 9a82050b35b556afaa7c8948810baa3f1e4a9079
issue: Resolution Settings original binding evidence; no runtime claims
hypothesis: source-only delegate evidence gate accepts internally impossible count combinations, allowing a false provenance PASS.
files: scripts/t5_validate_resolution_delegate_probe.py; scripts/test_t5_validate_resolution_delegate_probe.py; own work and session files only.
experiment_key: T5-RES-DELEGATE-COUNT-INVARIANTS-20261111
shared_resource: none; Python-only; no Unity, APK, T4 mouse files, or Settings changes.
expected_sha_policy: branch head read before each change; GitHub contents API conditional blob SHA; no force.
status: source_patch_and_regression_committed; CI_unverified
result: scripts/t5_validate_resolution_delegate_probe.py now rejects option delegate method count exceeding two authenticated original delegate sites; added four source-only regression tests. Commits 4475971c6ab955f9cbe03c1a5cdf45b4c83566f9 and dc5e88697812f8879a0d4f18d8e0a6b4389fd902. No CI/device execution claimed.\nnext: run python -m unittest scripts.test_t5_validate_resolution_delegate_probe on CI or checked-out repo, then investigate original Settings runtime binding separately.
