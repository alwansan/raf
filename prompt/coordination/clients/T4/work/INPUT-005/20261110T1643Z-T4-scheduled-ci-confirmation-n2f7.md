# T4 INPUT-005 — CI confirmation scope
session_id: 20261110T1643Z-T4-scheduled-ci-confirmation-n2f7
origin: scheduled
issue_id: INPUT-005
base_sha: ceeb2cedb8d586f196effa9c9c897b8443239505
status: active
updated_at: 2026-11-10T16:43:30Z
intended_files: this work file; separate T4 session checkpoint
experiment_key: eligibility-epoch-python-regression@9a9db82ad048bcfc2994917a05981eb31d5f87bd/run-42846576303
resource_key: none (read-only existing source-only CI)
hypothesis: prior epoch regression CI was unverified; existing workflow run resolves verification without repeating CI.
constraints: no Unity build; no game input or .rgd modifications; T5 owns resolution.
Evidence: https://github.com/alwansan/raf/actions/runs/42846576303 completed success; classifier-source-only job success, including epoch unittest discovery.
Next: read signed device logs with new classifier, distinguish Android pointer capture from Raft gameplay click/wheel handling.
