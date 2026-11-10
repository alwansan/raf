# T4 INPUT-005 — CI proof checkpoint
session_id: 20261110T0841Z-T4-scheduled-ci-proof-k4r8
origin: scheduled
issue_id: INPUT-005
status: active
base_sha: c32eeafc4a3097a4944fa4ef6f9466279a7ce855
intended_files: prompt/coordination/T_TEAM/work/20261110T0841Z-T4-scheduled-ci-proof-k4r8.md; prompt/coordination/clients/T4/sessions/20261110T0841Z-T4-scheduled-ci-proof-k4r8.md
experiment_key: t4-capture-eligibility-contract@7d3f11ecd1f022f52240a15e6ec4c002636cae62+ubuntu24.04+python-unittest
resource_key: none (reuse completed CI, no dispatch)
updated_at: 2026-11-10T08:41:00Z
hypothesis: Previously unverified four capture eligibility regression checks are now exercised by existing CI.
evidence: https://github.com/alwansan/raf/actions/runs/42776921454 — completed success; job classifier-source-only; step Verify source-only classifier regression suite success. Workflow executes three unittest discovery commands and py_compile, including test_t4_capture_eligibility_contract.py.
limits: no device input, no Unity runtime, no signed Raft mouse validation. Preserve owner-confirmed world save/reload on artifact 42058825739.
next: inspect Android/Unity input bridge with a new isolated hypothesis; use device JSONL to test actual buttons and scroll. No redundant CI.
