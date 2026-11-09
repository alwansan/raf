# T4 scheduled — escaped-comment analyzer runtime repair

- session_id: 20261109T0237Z-T4-scheduled-analyzer-comment-v3q7
- origin: scheduled
- identity: T4
- issue: INPUT-005 OPEN / device pending
- initial HEAD: 34d758899e8e2ac0794461846334b51ad2b7e2ae
- resumed from: 20261109T0209Z-T4-chat-unity-legacy-readers-w7q5; 20261109T0143Z-T4-scheduled-capture-phase-j6r2
- work: prompt/coordination/B_TEAM/work/INPUT-005/T4-20261109T0237Z-scheduled-analyzer-escaped-comment.json
- experiment: T4-analyzer-literal-escaped-newline-runtime-regression-v1
- resource: T4-Python-analyzer-only-no-Unity-CI

## Finding and changes

Read owner DEVICE_FEEDBACK_42058825739_AR, owner requirements, T_TEAM protocol, T4 memory and latest chat sessions, and current source. Source `scripts/t4_analyze_mouse_lab_routes.py` contained literal backslash-n sequences inside a Python comment immediately before `key = ...`, so the assignment was swallowed by the comment. Any valid physical mouse input then reached `groups[key]` with `key` undefined, producing NameError; its exception handler does not catch NameError. This is a deterministic source defect, not a claim of Android test failure.

- Scope commit f9da0967f9eb4750cabd8bb8b155f539154e7529.
- Fix commit 95d8556ff35628dad6bfdaf098c7149c5b576fc5: replace literal escaped newlines with actual line breaks, restoring the capture-phase key assignment.
- Regression commit f0d68d1d778e869ac99840096c0060ae83163956: request ON plus unknown, explicit false and true callbacks must classify into three independent phases.
- Read-only Actions: recent 42550454759, 42550454734 success; no duplicate Actions started.
- CI not run for this change. Container GitHub DNS resolution failed (`Could not resolve host: github.com`); connector source edits succeeded. The new test is unexecuted; avoid claiming green.
- No Unity, game runtime, T5 unified Mini, keyboard, touch, save .rgd, audio or Settings changes.

## Evidence and next step

Owner's phone run 42058825739 confirmed world creation, save, exit and reopen for that artifact, despite packaging publication failure. Preserve LOCAL-005 as OPEN for remaining cases. Real owner CL uncaptured mouse callbacks proved LEFT and vertical wheel only; captured=true three buttons/wheel remains missing. The later T4 game-source bridge/reader telemetry CI42549986761 succeeded in source-only checks, not phone.

Next: execute `python -m unittest tests.test_t4_analyze_mouse_lab_routes` in connected CI or local checkout; inspect fresh CL/test captured=true mouse callbacks; compare Android native callback to Unity Legacy reader telemetry in same signed Raft candidate. No new Mini build requested. INPUT-005 OPEN, game NOT_READY 0/3.
