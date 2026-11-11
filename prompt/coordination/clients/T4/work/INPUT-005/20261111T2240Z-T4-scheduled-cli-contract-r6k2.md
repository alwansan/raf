# INPUT-005 T4 CLI regression scope
session_id: 20261111T2240Z-T4-scheduled-cli-contract-r6k2
origin: scheduled
start_head: fbc49f9c127ea16d0e295a6dc8d899774de12ab2
experiment_key: INPUT-005-cli-exit-contract-r6k2
files: tests/test_t4_gap_classifier_cli.py; prompt/coordination/clients/T4/sessions/20261111T2240Z-T4-scheduled-cli-contract-r6k2.md
hypothesis: JSON summary CLI must remain executable and fail-closed for malformed/reset telemetry, not only through direct classify() unit tests.
shared_resource: none; no Unity/Android build; no shared game files.
Evidence: DEVICE_FEEDBACK_42058825739_AR.md confirms world save/reopen on 42058825739; 8 Nov owner mouse movement works, clicks/scroll remain unproven. Prior T4 20261111T2140Z reset gate source/tests committed but unexecuted in that run.
