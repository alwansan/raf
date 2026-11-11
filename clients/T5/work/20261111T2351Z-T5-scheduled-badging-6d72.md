# T5 work 20261111T2351Z-T5-scheduled-badging-6d72
session_id: 20261111T2351Z-T5-scheduled-badging-6d72
origin: scheduled
base_sha: b2cc78a3aeab615a5ddc63fa70c52512f38c8a9f
status: waiting_ci
issue_id: APK-OBB-BADGING-UNIQUENESS
intended_files: scripts/t5_verify_apk_obb_pair.py, tests/test_t5_verify_apk_obb_pair_badging.py, clients/T5/sessions/20261111T2351Z-T5-scheduled-badging-6d72.md
experiment_key: t5-apk-badging-duplicate-identity-v1-b2cc78a3
resource_key: none (Python only)
hypothesis: BADGING.search accepts ambiguous duplicate package identity lines; aapt must return exactly one package declaration for provenance.
Coordination: no Unity, no T4 input, no shared Settings source; preserve original owner phone evidence. Validate synthetic badging and reject duplicate identities.

Results: verifier commit e3d9689f4f69d56ce5510f5f4842766a167a9b9a; regression test commit 55ec3bfc37609252fc5ab8ec97d5223e9ce9a161; session checkpoint commit 80510a46eb43a075e01f922eb92a89f49b97c660. CI https://github.com/alwansan/raf/actions/runs/43123065340 was in_progress on intermediate SHA. Final SHA tests pending independent verification. No device claim.
