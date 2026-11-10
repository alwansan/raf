# T2 scoped work — 20261110T2315Z-T2-scheduled-producer-contract-k7m2
origin: scheduled
issue_id: WATER-001
base_sha: ba0be646bf3d6557e1d3a34c220e80f3d6f10469
status: active
experiment_key: t2-foam-public-product-allowlist-regression-python311-20261110
resource_key: none (source-only CPU test)
intended_files: .github/workflows/raft-t2-foam-evidence-cli-gate.yml; prompt/coordination/clients/T2/sessions/20261110T2315Z-T2-scheduled-producer-contract-k7m2.md; this work file
hypothesis: the existing Foam public producer JSON schema privacy test is not executed by the Foam evidence CLI CI gate, leaving an independently existing regression unmonitored.
preconditions: owner device report 42058825739 read; current workflow explicitly tests only test_t2_foam_evidence*.py; test_t2_foam_json_product_guard.py exists and tests compare_private_names public schema.
validation: extend path filter to producer and producer guard; execute both suites without original assets. No claim of publisher integration, ShaderLab or Android proof.
taken_over_from: scripts/t2_foam_texture_identity.py and tests/test_t2_foam_json_product_guard.py, original T2 work; previous CI 42904487022.
