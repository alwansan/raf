# T5 scheduled scope
session_id: 20261107T1751Z-T5-scheduled-s7k4
origin: scheduled
issue_id: PERF-007
baseline_sha: aaee392ea6072d6e799f1fc89559cfe81e7b4b10
intended_files: scripts/t5_unity_interval_epoch.py; tests/test_t5_unity_interval_epoch.py
hypothesis: concatenated JSONL sessions with identical scene/refresh/resolution are merged into one epoch, corrupting cross-session performance comparisons.
experiment_key: T5-jsonl-session-boundary-epoch-20261107
resource_key: none
status: waiting_ci
source_fix_sha: 58bb975bb674912c1f379a03980ec5ce7ba2d1d1
test_commit_sha: 599a73841cdd0d369d069befa95c8e51382f5051
checkpoint_sha: c4aba8e501fa7f123aa076ac654dfdf7da712d5d
validation: static review; CI/Python tests not yet verified
next_step: run test_t5_unity_interval_epoch.py and inspect results; compare separate LogRaft sessions only when source APK/OBB identity verified
No Unity or shared device resources; T4 mouse files untouched.
