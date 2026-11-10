# T4 scheduled checkpoint — 2026-11-10 01:40 UTC
session_id: 20261110T0140Z-T4-scheduled-cl-missing-input-v8q2
origin: scheduled
resumed_from_sessions: 20261110T0042Z-T4-scheduled-capture-device-boundary-p7x4.md; 20261109T2335Z-T4-scheduled-mouse-game-boundary-v3k8.md
baseline_sha: 613ab7179416d640a7751ac37a5e6c83656854bc
scope_commit: f90bffa32fa7cdab02cedd53e3d2e12afb2fc7b7
work: prompt/coordination/T_TEAM/work/20261110T0140Z-T4-scheduled-cl-missing-input-v8q2.md
issue: INPUT-005 OPEN

## New decisive CL audit
Read latest CL/test shared-20261109-233132-554663211 summary from main and inspected directory. Session 20261109-233132-554663211, app_source 731d7a68bb3826b348d0314f694737b522e92976, pack SHA256 9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6. All NINE T4 cases T4-01..T4-09 are **NEEDS_INPUT**, observed exactly 'User action, mouse/file or judgment is required'. This is NOT a mouse PASS, NOT a failure of actual button delivery, and NOT game-side proof. T1 5, T2 4, T3 6, T5 6 entries are separate tests and cannot substitute for T4 physical input evidence. Latest CL folder contains T3 screenshots, shared events and T2 GLES traces, not a signed Raft same-process mouse-to-game trace.

Source: https://github.com/alwansan/CL/blob/main/test/shared-20261109-233132-554663211/summary-20261109-233132-554663211%20(1).json
Current branch at initial check: 613ab7179416d640a7751ac37a5e6c83656854bc. Recent T3 CI 42728727179 success (unrelated to mouse). Owner-confirmed LOCAL-005 world/create/save/reopen remains limited to artifact 42058825739 and original .rgd unchanged.

## Result and next
Evidence classification completed; no Unity edits, CI rerun, APK build, touch changes or T5 Resolution edits. Existing testpack already includes nine T4 tests; do not create duplicates. Next practical step: capture real physical mouse gestures in the shared mini lab T4-01..09 (or signed-game capture where possible) and correlate per-button down/up + wheel axes with Unity Legacy Input and game reaction. Preserve keyboard and cursor focus transition; if device report lacks trace, record NEEDS_INPUT, not PASS. Once specific failing boundary is demonstrated, fix bridge source in a separately coordinated scope.
