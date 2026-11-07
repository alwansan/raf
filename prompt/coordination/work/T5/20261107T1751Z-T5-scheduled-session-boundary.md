# T5 scheduled scope
session_id: 20261107T1751Z-T5-scheduled-s7k4
origin: scheduled
issue_id: PERF-007
baseline_sha: aaee392ea6072d6e799f1fc89559cfe81e7b4b10
intended_files: scripts/t5_unity_interval_epoch.py; tests/test_t5_unity_interval_epoch.py
hypothesis: concatenated JSONL sessions with identical scene/refresh/resolution are merged into one epoch, corrupting cross-session performance comparisons.
experiment_key: T5-jsonl-session-boundary-epoch-20261107
resource_key: none
status: active
No Unity or shared device resources; T4 mouse files untouched.
