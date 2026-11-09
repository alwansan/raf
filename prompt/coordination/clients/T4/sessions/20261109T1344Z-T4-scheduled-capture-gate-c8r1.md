# T4 scheduled — capture evidence gate (9 Nov 2026 13:44 UTC)

- session_id: `20261109T1344Z-T4-scheduled-capture-gate-c8r1`
- origin: `scheduled`; branch: `feature/android-native-port`.
- resumed_from: `20261109T1239Z-T4-scheduled-device-gate-h6r2`, `20261109T1142Z-T4-scheduled-capture-evidence-q4m8`, original game bridge CI42518143297.
- scope commit: `4cf9c0ec065fdc49a5be3da45917075b29906178`.
- source commit: `efb7e396ef0b9776ffbdc96efce901484469849d`.
- test commit: `a3ec71c0603b1be2b10eded3e32ebee02a976276`.
- experiment_key: `T4-INPUT005-captured-android-vs-unity-evidence-gate-v1`.
- intended files: `scripts/t4_capture_acceptance_gate.py`, `tests/test_t4_capture_acceptance_gate.py`, this session.

## Baseline
Read live AGENTS.md, owner requirements, STATUS, 5 Nov owner device report, T_TEAM collaboration and operating instructions, T4 memory and last scheduled checkpoint. Owner artifact 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628) confirmed world enter/save/exit/re-enter; publishing failed, not gameplay. Newer original mouse bridge source-only CI42518143297 passed; CL 8 Nov physical mouse mini callbacks captured=false and no matching Unity consumer device evidence. Do not conflate source and phone evidence. T5 owns shared Mini/Resolution/buttons; T4 owns physical captured game mouse.

## This cycle
Added a **standalone fail-closed evidence triage** for existing `scripts/t4_analyze_mouse_lab_routes.py` JSON output. It refuses to classify uncaptured callbacks or capture_request=ON alone as captured input. Even complete captured LEFT/RIGHT/MIDDLE press-release and V/H wheel are labeled **CALLBACK_ONLY** / **CALLBACK_PAIR_ONLY**, never Unity or device PASS. Five source regressions were added covering uncaptured data, ON without callback, complete callbacks, incomplete pair and inconsistent route. No game source, Unity bridge, keyboard, touch, .rgd, audio or Settings changed.

## Verification and limits
Files published through GitHub connector; **tests not executed in this run** (local GitHub DNS failure, no CI dispatched). GitHub connector does not enumerate running/queued Actions and did not list CL latest tree; prior pinned evidence only. No new signed full-game APK, no Android hardware test, no assertion of captured clicks in Raft. No equivalent Unity build launched or canceled.

## Next
Run `python -m unittest discover -s tests -p 'test_t4_capture_acceptance_gate.py'` on a source checkout, and run analyzer + gate on same-version real captured Android log. Require separate original Raft Unity Legacy Input consumption and visible action, plus keyboard/focus/menu cursor/world save regression on one signed candidate. INPUT-005 OPEN; LOCAL-005 owner-confirmed on old artifact only; game NOT_READY 0/3.
