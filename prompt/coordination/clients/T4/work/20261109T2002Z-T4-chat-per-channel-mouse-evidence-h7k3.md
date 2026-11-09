# T4 per-channel mouse evidence scope
session_id: 20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3
origin: chat
updated_at: 2026-11-09T20:02:00Z
status: active
issue_id: INPUT-005
base_sha: 99c25340edb45bbd18d4a33ed9937d0679e7114f
resumed_from_sessions: 20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6; 20261109T1939Z-T4-scheduled-reader-poison-q8m5
experiment_key: T4-INPUT005-genuine-Android-pressMask-unity-reader-channel-correlation-v1-Unity2021
resource_key: none (isolated source-only test)
intended_files:
- scripts/t4_correlate_mouse_runtime_epochs.py
- scripts/tests/test_t4_correlate_mouse_runtime_epochs.py
- prompt/coordination/clients/T4/sessions/20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3.md
- prompt/coordination/clients/T4/work/20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3.md
- prompt/coordination/experiments/T4/20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3.json
- prompt/coordination/B_TEAM/events/T4/20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3.json
scope: Add conservative per-button and per-wheel-axis SOURCE-only candidate telemetry using original producer pressMask/releaseMask and 11 exact reader slots; fail closed if missing/invalid slot evidence, never infer actual gameplay. Preserve existing aggregate status and CI, guard against nonmatching button channels.
recovered_evidence: CI42687110814 PASS 30/30; latest CL/test/shared-20261109-225506-552476830 using 0.2.14-shared, 30 cases, nine T4 NEEDS_INPUT; no actual same-source full Raft physical mouse proof.
coordination: Checked live branch HEAD and zero queued/in_progress Actions before reservation. Independent from T5 shared Mini r4 build, T1 compute, T2 Foam, T3 shaders. Do not touch game/Android/Unity sources, existing unified Mini, team pack or native build request.
