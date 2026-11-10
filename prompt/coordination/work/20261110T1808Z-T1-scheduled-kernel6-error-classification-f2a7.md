# T1 scope — 20261110T1808Z-T1-scheduled-kernel6-error-classification-f2a7
origin: scheduled
issue_id: WATER-001
base_sha: 55534e30c8efc54d93f20e68b7980e8a484273aa
status: completed_source_only_test_pending
experiment_key: kernel6-error-vs-mention/CL-520c4cf/scan-v2
resource_key: none (source-only)
intended_files: scripts/t1_kernel6_log_context.py; tests/test_t1_kernel6_error_classification.py; prompt/coordination/clients/T1/sessions/20261110T1808Z-T1-scheduled-kernel6-error-classification-f2a7.md
hypothesis: current KERNEL6 matching counts informational mentions as errors; distinguish strict error-context lines without rewriting historical counts or claiming kernel identity.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md, CL@520c4cf, script t1_kernel6_log_context.py.
coordination: T4 owns physical mouse, T5 owns Resolution and package delivery; no modifications there. No Unity/CI build.

result_commits: 5355bbcf6661770ac56ec74bbfc870761f6c7c05, 0631eba80b39549904f1fb75e3c16243cda838b4
session_commit: 224e4e32e2c799f782055d28f192dbb902eb353f
validation: not_run (local DNS failure; no duplicate CI)
next: run regression, then classify real CL logs per session; obtain original FindKernel/Dispatch binding.
