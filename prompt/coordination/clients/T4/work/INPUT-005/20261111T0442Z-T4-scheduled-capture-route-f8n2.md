# T4 INPUT-005 captured-button path audit
session_id: 20261111T0442Z-T4-scheduled-capture-route-f8n2
origin: scheduled
issue_id: INPUT-005
status: active
intended_files: tests/test_t4_captured_action_contract.py; this work file; own session file
experiment_key: t4-captured-action-callback-contract-v1/android-2021-legacy
resource_key: none (source-only)
resumed_from_session: 20261111T0335Z-T4-scheduled-input-acceptance-n7q3
hypothesis: captured button/scroll callbacks may be recorded but fail to reach original Raft Legacy Input wrappers; verify source route independently of pointer movement.
Owner evidence: 2026-11-08 mouse camera moves, LEFT/RIGHT/MIDDLE/scroll absent. 2026-11-05 world/save/reopen on artifact 42058825739 remains accepted only for that artifact.
Safety: no changes to game assets, keyboard, touch, .rgd, sound, Settings, T5 Resolution; no heavy CI or build.
