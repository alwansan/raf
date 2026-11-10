# T4 checkpoint — 20261110T1240Z-T4-scheduled-mouse-evidence-v9k3
origin: scheduled
base_sha: a1184a61eb2f4fb33e83f1527ab5310fbb287009
scope_commit: 2ed6f82f908283bc9423d368ff35789a08bb9ea1
resumed_from: 20261110T1135Z-T4-scheduled-device-evidence-m4q8; 20261110T1036Z-T4-scheduled-native-device-gate-b7q2
work: prompt/coordination/clients/T4/work/INPUT-005/20261110T1240Z-T4-scheduled-mouse-evidence-v9k3.md

Read owner report docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md and T_TEAM live operating/coordination documents. Rechecked AndroidPhysicalMouseCapture.cs and newest T4 session. Latest HEAD before write a1184a61eb2f4fb33e83f1527ab5310fbb287009 (T3 commit at 2026-11-10T12:27:27Z). CL/test directory newest shared-20261109-233132-554663211; CL main b3286b326d73ee511cd2f68a43c92a1233c2f8d1. No newer game input device proof. Recent Actions T5 audit run 42802257348 completed success, unrelated to gameplay mouse. No duplicate build or CI requested.

Engineering deliverable: new isolated, falsifiable signed-game trace plan with six failure boundaries, explicitly distinguishing native callback, buffered frame, Legacy getter and actual gameplay action, and preserving keyboard, Escape, .rgd, Settings, audio and T5 Resolution ownership. This is a source/trace decision aid, NOT a mouse behavior fix or device PASS. Existing T4 CI42776921454 remains source-only PASS. Owner's 42058825739 world enter/save/exit/reopen success is retained only for that artifact; LOCAL-005 and INPUT-005 remain OPEN, NOT_READY 0/3.

Next: read latest CL/test and signed-game input trace; classify earliest failure against work file; if none, add focused frame-boundary regression using existing test infrastructure rather than another speculative runtime patch. No original game assets or secrets published.
