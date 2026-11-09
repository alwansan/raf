# T4 scope reservation
session_id: 20261109T1939Z-T4-scheduled-reader-poison-q8m5
origin: scheduled
baseline_sha: 896547525db6b02e299bd73e782450a65fa04de4
issue: INPUT-005
experiment_key: T4-INPUT005-poisoned-logger-reader-only-exclusion-v1
resource_key: none (Python source gate only)
owned_paths: scripts/t4_correlate_mouse_runtime_epochs.py; scripts/tests/test_t4_correlate_mouse_runtime_epochs.py; own session and work only.
hypothesis: reader_only counts poisoned JSONL logger sessions although matched/callback_only correctly exclude them; this can claim an unattributed getter from replayed/corrupted session. Exclude poisoned scopes consistently and test with real JSONL shape. Preserve source-only and device_pass=false. No Unity build, no other T worker files.
