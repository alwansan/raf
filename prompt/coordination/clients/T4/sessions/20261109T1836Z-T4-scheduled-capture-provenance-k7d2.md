# T4 scheduled session — 20261109T1836Z-T4-scheduled-capture-provenance-k7d2
origin: scheduled
start_head: 55b2475e7cef2a59321ba30d8f11b6b2f7cad16f
scope_commit: ee849ac0f7eff042ac003199118e4deca167476d

## Verified
- Owner device feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628, world entry/save/exit/reopen succeeded on device; package publishing failed. No extrapolation to later builds.
- 8 Nov T4 original captured button/wheel fallback source compiled on CI42518143297 (111 C# and 9 Python assertions), but no signed full-game phone acceptance. Existing owner CL/test physical mouse evidence was uncaptured; later owner reports camera movement while captured, no in-game buttons/wheel.
- Prior T4 gate runtime CI42657857161 succeeded eight tests on source 1648b33f. This validates the diagnostic gate only.
- Current live HEAD read at 55b2475e7cef2a59321ba30d8f11b6b2f7cad16f; recent T2 Foam CI42673027759 failed (not T4-owned). No equivalent CI repeated.
- Inspected scripts/t4_capture_acceptance_gate.py: triage explicitly returns unity=UNVERIFIED and device_pass=false; no false device pass is claimed.

## Result and limits
Created an isolated scope record for precise callback-to-consumer correlation; no Unity/game source edits or CI were justified by current evidence. No actual new Android captured-button log with same-build Unity consumer trace was available in this review. This is a recorded evidence gap, not a fix to INPUT-005.

## Continuation
Read latest HEAD and active T4/T5 scopes. Identify authenticated source location for per-frame legacy adapter consumer logging without altering input state. On a new signed game candidate collect same-build captured LEFT/RIGHT/MIDDLE, vertical/horizontal wheel, focus transitions, Raft cursor and keyboard, world save/reopen. Compare with Unity frame-consumer counters. Preserve .rgd, keyboard, audio, Settings; T5 owns Resolution/three UI buttons. INPUT-005 OPEN, full-game NOT_READY 0/3.
