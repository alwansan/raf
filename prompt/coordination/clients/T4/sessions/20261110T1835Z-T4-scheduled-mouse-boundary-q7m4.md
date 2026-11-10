# T4 scheduled session — 2026-11-10 18:35 UTC
session_id: 20261110T1835Z-T4-scheduled-mouse-boundary-q7m4
origin: scheduled
base_head: 5337664c7ba1fd813bc11a2e134e18a62e74c43f
scope_commit: addcc0f5ca5f5bf406859db85aea7e5d37fb5f24
implementation_commit: 4a1ff04511a4e71b1572ebc748d29af7c39b993b
scope: prompt/coordination/clients/T4/work/INPUT-005/20261110T1835Z-T4-scheduled-mouse-boundary-q7m4.md
script: scripts/t4_mouse_boundary_trace.py
previous: prompt/coordination/clients/T4/sessions/20261110T1736Z-T4-scheduled-cl-evidence-j8p2.md

## Evidence and result
Read AGENTS, owner requirements, STATUS, device feedback, team coordination/operating model, and prior T4 session. Current branch HEAD at entry 5337664c7ba1fd813bc11a2e134e18a62e74c43f. Source-only CI 42846576303 previously successful. New helper implements a conservative, opt-in T4_MOUSE_STAGE frame/stage/button trace contract for android, unity and raft, across left/right/middle/wheel. It records stage evidence and same-frame gaps without falsely calling absent events failures. Includes self-test runnable with `python scripts/t4_mouse_boundary_trace.py --self-test`. GitHub Actions not dispatched; local runtime test not performed in this session.

## Boundaries
Owner confirmed world enter/save/exit/reenter on artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628. Publication failed. Do not regress .rgd, FileManager, keyboard, audio, Settings. Owner's newer feedback says camera movement works but click/wheel do not. This helper does not instrument runtime, fix click mapping, prove device behavior, or alter Resolution (T5). It needs actual signed-build stage markers; absent markers are inconclusive. No heavy build, release or duplicate CI.

## Next
Run self-test and add guarded native/Unity/Raft stage emitters with bounded sampling only after reviewing live AndroidPhysicalMouseCapture.cs and owner log path; compare timestamps and frame numbers, focus/reacquire and keyboard. Then fix the first proven break and validate on device. INPUT-005 remains OPEN.
