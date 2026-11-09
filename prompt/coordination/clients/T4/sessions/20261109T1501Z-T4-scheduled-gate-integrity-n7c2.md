# T4 INPUT-005 — captured evidence validation

- session_id: `20261109T1501Z-T4-scheduled-gate-integrity-n7c2`
- origin: scheduled
- resumed_from_session: `20261109T1344Z-T4-scheduled-capture-gate-c8r1`
- scope commit: `6328283ffd5d3088c56c83041da451fe4c4fa2fd`
- source commit: `b6cf40f9019c232f08c30f6e9df6f3bba9f24e01`
- tests commit: `a4abe80f8ad9ca3e6405d4bf7bd9f86a7dcd879a`
- origin evidence: owner world/save/reopen artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628; newer 8 Nov feedback confirms camera pointer capture but mouse LEFT/RIGHT/MIDDLE and wheel still fail.
- experiment_key: T4-capture-gate-malformed-android-evidence-v2
- intended_files: scripts/t4_capture_acceptance_gate.py, tests/test_t4_capture_acceptance_gate.py, this session and unique work file.

## Engineering change
The evidence gate previously accepted `routes="captured"` because Python substring membership returned true, and could misinterpret `button_presses_observed="left"` or boolean scroll counters as legitimate captured callbacks. It now requires a list of string routes containing `captured`, button arrays of known button names, and nonnegative integer (not bool) wheel counters. Five negative-control regressions were added. Existing callback-only classification and `unity=UNVERIFIED` remain unchanged.

## Evidence boundary
Code and tests published through GitHub connector. **No tests executed**, no Android device run, no Unity build or new APK; container GitHub DNS lookup failed, and connector has no general workflow run listing. Latest full HEAD and CL uploads not exhaustively verified. Do not claim mouse input fixed or accept phone PASS. Keyboard, game code, original .rgd, audio, Settings, T5 Resolution and UI were untouched.

## Next
Execute `python -m unittest discover -s tests -p 'test_t4_capture_acceptance_gate.py'` in CI/checkout; inspect actual captured=true device logs from one signed candidate and correlate with Unity Legacy Input Mouse0/1/2 and scroll, then in-game response. Preserve successful local world save/reopen and keyboard regression. INPUT-005 remains OPEN; LOCAL-005 historical owner success only.
