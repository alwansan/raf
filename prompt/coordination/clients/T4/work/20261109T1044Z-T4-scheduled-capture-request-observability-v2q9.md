# T4 INPUT-005 — capture request observability
session_id: 20261109T1044Z-T4-scheduled-capture-request-observability-v2q9
origin: scheduled
base_head: bbce0ed66026db03eda86fea3d34383968e3a063
scope: scripts/t4_analyze_mouse_lab_routes.py; scripts/tests/test_t4_capture_request_observability.py; own session file only
hypothesis: analyzer discards capture_request ON/OFF and cannot distinguish unattempted capture from requested-but-no-captured-callback; add counts without inferring capture success.
experiment_key: T4-capture-request-observability-20261109
shared_resource: none; no Unity/mini build
owner evidence: DEVICE_FEEDBACK_42058825739_AR.md; successful local world/save/reload preserved. Newer owner CL mini has uncaptured mouse but no captured proof.
coordination: T5 owns shared mini, display/layout/resolution; T4 parser-only. Preserve keyboard/.rgd/audio/Settings. No actions cancelled.
status: planned
