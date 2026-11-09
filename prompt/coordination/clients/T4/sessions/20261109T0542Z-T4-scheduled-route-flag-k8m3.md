# T4 INPUT-005 checkpoint — 20261109T0542Z-T4-scheduled-route-flag-k8m3
- session_id: 20261109T0542Z-T4-scheduled-route-flag-k8m3
- origin: scheduled
- base_sha: 52638314d4fb9151e3fce0639d27457379808aa4
- resumed_from_sessions: 20261109T0344Z-T4-scheduled-route-consistency-n8q2.md; 20261109T0209Z-T4-chat-unity-legacy-readers-w7q5.md
- issue_id: INPUT-005 (OPEN)
- experiment_key: T4-route-flag-bidirectional-contradiction-20261109
- scope: scripts/t4_analyze_mouse_lab_routes.py; tests/test_t4_analyze_mouse_lab_routes.py
- plan_commit: ca12359f74c510e3eb3e6e5e8fc16cc7eaef5dfa
- implementation_commit: 743631d8337a46455ce473519d9b25749641f072
- test_source_commit: e70fb94b7879747ff17e75eb157ec8e58486524f

## Result and limits
A contradictory Android callback tagged route=captured with captured=false previously counted as uncaptured physical mouse evidence. Analyzer now rejects both contradictory directions, preserving explicit unknown capture flag as unknown; added two regression tests. No CI or local Python test execution: local git network DNS failed. Source-only code/test published, not runtime verified. Do not claim device mouse buttons/wheel fixed.

Owner phone artifact 42058825739 successfully entered/saved/exited/reentered a local world; preserve .rgd and LOCAL-005 device evidence. No changes to game, keyboard, Unity, OBB, audio, Settings, T5 mini UI or resolution. T5 owns shared mini build. Existing CL physical mouse uncaptured evidence remains distinct from captured=true and game Unity Legacy consumption. Next: run test_t4_analyze_mouse_lab_routes.py in available CI or runner, inspect fresh CL/test captured=true + Android/Unity paired telemetry; do not duplicate running Actions.
