# T4 scheduled checkpoint — 20261110T1338Z-T4-scheduled-eligibility-classifier-p6v4
origin: scheduled
base_head: 36661a7ccbc8bd2279eb89a19ad4dfff9fd005a4
resumed_from: 20261110T1240Z-T4-scheduled-mouse-evidence-v9k3
scope: prompt/coordination/clients/T4/work/INPUT-005/20261110T1338Z-T4-scheduled-eligibility-classifier-p6v4.md
scope_commit: 4ad6e024ab9cfb360532da070dbfcb29e53d326c
script_commit: f78acab072b875ba3eac24f137438410aaa388a3
test_commit: 9de8675f6c534e326edb11b7e748b518ce94bec8

Read owner report, AGENTS, owner requirements, STATUS, T_TEAM live operating rules, and latest T4 session. CL/test latest shared-20261109-233132-554663211 (no newer signed-game mouse proof in this listing). Latest inspected Actions include T5 42819012779 success and T4 classifier 42776921454 success; neither proves actual mouse clicks. Source AndroidPhysicalMouseCapture.cs currently logs physical_mouse_capture_eligibility transitions. No runtime code change.

New independent diagnostic: scripts/t4_diagnose_mouse_eligibility.py consumes that marker, classifies last observed eligibility gate vs request/callback evidence and explicitly refuses to call it phone/gameplay PASS. Added seven source-free regression cases in tests/test_t4_diagnose_mouse_eligibility.py. Files published without editing shared workflow, Unity, touch, keyboard, original .rgd, audio, Settings, or T5 Resolution. No new CI/build was dispatched. Test suite not executed in this connector-only run; needs python3 -m unittest tests.test_t4_diagnose_mouse_eligibility, and inclusion in existing T4 workflow after review if useful.

Owner-confirmed local world enter/save/exit/reopen is retained only for artifact 42058825739 / source e9c358eda01785b65e4eb14f18723da426635628. INPUT-005 and LOCAL-005 remain OPEN, device buttons/wheel not verified. No claim that missing telemetry proves Android denial.

Next: run seven unit tests; apply analyzer to fresh signed Raft input log from CL/test or CL/raft log, correlate epoch-specific request/callback/Legacy reader events with gameplay, then fix the first confirmed boundary. Coordinate with T5 for single shared mini APK only if actual runtime probe is needed. Do not duplicate Actions.
