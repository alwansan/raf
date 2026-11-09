# T4 scheduled session — 2026-11-09 15:47 UTC
session_id: 20261109T1547Z-T4-scheduled-gate-execution-x9b4
origin: scheduled
baseline_sha: 5e2d9a8af78c1bcfb1d3f1dc5b39c14b2ee78d5c
last_checked_head: 6a3b59b9ce57979aafa600d480bf0da5ae18e078
work: prompt/coordination/work/INPUT-005/T4-20261109T1547Z-T4-scheduled-gate-execution-x9b4.md
implementation: scripts/tests/test_t4_capture_acceptance_gate_runtime.py
commits: 366d6beba9b7847f3730df1708b86b6941673858; 6a3b59b9ce57979aafa600d480bf0da5ae18e078
status: SOURCE_TEST_ADDED_NOT_EXECUTED
evidence: inspected existing scripts/t4_capture_acceptance_gate.py and owner DEVICE_FEEDBACK_42058825739_AR.md; 8 regression methods test callback-only versus Unity/device pass, absent capture, unpaired buttons, wheel, malformed route/button/count/envelope.
CI: no equivalent Unity/mini build launched; latest checked run 42645204502 was T2 Foam SUCCESS, not T4.
limits: no authenticated physical mouse captured game run, no phone test, no claim of buttons fixed. World/save/reopen owner pass applies ONLY to 42058825739; LOCAL-005 remains OPEN, INPUT-005 OPEN.
next: execute python -m unittest discover -s scripts/tests -p test_t4_capture_acceptance_gate_runtime.py -v, fix any failures, then compare new signed-game captured=true logs with actual Unity Legacy Input calls. Keep keyboard, .rgd, audio, Settings and T5 Resolution/overlay untouched.
