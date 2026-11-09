# T3 scoped work — SPIR-V Location uint32 contract
session_id: 20261109T2332Z-T3-scheduled-spv-location-bound-f4k9
origin: scheduled
issue_id: RENDER-002
base_sha: 8cf4fdc75a89987b62eabe396ee1f11fd197a1b0
resumed_from_sessions: 20261109T2226Z-T3-scheduled-used-lane-superset-q8m3; 20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2
intended_files: scripts/t3_smoke34_location_provenance_gate.py; tests/test_t3_smoke34_location_provenance_gate.py; own work and session
experiment_key: t3-source-free-spv-location-uint32-overflow-negative-v1
resource_key: none (no ZIP2/Unity/CI shared runner)
hypothesis: SPIR-V Location is a 32-bit unsigned literal, but synthetic provenance gate accepts unbounded Python integers. Reject overflow before any structural pass, without treating structural pass as authentic provenance.
status: active
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; latest 8 Nov shared mini policy.
concurrency: Latest checked Actions 42715257606/42715257589 completed failure in T5 integration; no duplicate builds; T4 mouse and T5 resolution excluded.
