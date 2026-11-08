# T1 WATER-001 work 20261108T0108Z-T1-scheduled-budget-test-path-f6c2
session_id: 20261108T0108Z-T1-scheduled-budget-test-path-f6c2
origin: scheduled
issue_id: WATER-001
status: active
updated_at: 2026-11-08T01:08:00Z
intended_files: scripts/test_t1_fft_capture_budget.py; prompt/coordination/clients/T1/sessions/20261108T0108Z-T1-scheduled-budget-test-path-f6c2.md; this work file
experiment_key: fft-capture-budget-regression-script-path-repo-branch-20261108
resource_key: none (source-only)
hypothesis: SCRIPT = Path(__file__).resolve().parents[1] / 't1_fft_first_divergence.py' resolves to repository root, not scripts/, causing all subprocess tests to fail before exercising budget guards.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner world/save/reenter success from run42058825739; CL water pass 23884/39132 and kernel 3850/6026; kernel6 identity not proven.
resumed_from: 20261107T2306Z-T1-scheduled-fft-budget-c8e2; latest prior dispatch coverage reported in chat.
coordination: isolated test file; no shader/runtime/meta/Unity/Actions changes. T4 physical mouse and T5 UI/Resolution remain separate.
plan: correct SCRIPT path, verify with source-only tests when possible, record exact limits and result.
