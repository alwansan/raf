# T4 session — 2026-11-09 09:36 UTC
session_id: 20261109T0936Z-T4-scheduled-parser-regression-r7v4
origin: scheduled
track: INPUT-005 / LOCAL-005 regression protection
status: source_test_added_unexecuted

## Verified inputs
- Owner report docs/DEVICE_FEEDBACK_42058825739_AR.md: actual owner device world entered, saved, exited, reopened from artifact 42058825739; preserve .rgd and do not confuse package publishing failure with gameplay.
- Current owner requirements 8 Nov: captured camera works, real buttons/wheel do not; T5 owns unified Mini and Resolution. No game-ready claim.
- Latest HEAD before work 8973a57f527e4651f6100e85a2991bd8afdf6b32 (09:33 UTC). Existing T4 memory/source bridge CI42518143297 successful source-only. CL/test listing inspected; no new captured=true proof established in this cycle.
- Source inspected: scripts/t4_analyze_mouse_lab_routes.py blob c345f3f56d6d89757eff525f820038e030a9d83b.

## Changes
- Independent scope prompt/coordination/clients/T4/work/20261109T0936Z-T4-scheduled-parser-regression-r7v4.md committed 3e02221d43c290b19b2af81584bb7fe2773ae9ea.
- Added scripts/t4_test_mouse_route_regression_r7v4.py commit c342684a967c5073e0261e7063586d01c1e7f43b. Five isolated unittest cases cover captured button press/release for LEFT/RIGHT/MIDDLE and both scroll axes, capture request not granted, contradictory route/flag pairs, malformed JSON envelopes/negative masks, and touchscreen/nonfinite scroll rejection. Assertions only test analyzer, never Unity gameplay.
- No modification of game source, touch, keyboard, .rgd, audio, Settings, T5 UI/Resolution, or shared CI.

## Validation / limitations
- GitHub connector write succeeded. Local container git access failed DNS (Could not resolve host github.com), so test suite has NOT been executed. No CI or APK started, no phone verification. Work status: test added, verification pending.
- To validate on checked-out repository: python3 scripts/t4_test_mouse_route_regression_r7v4.py. If PASS, run against real captured=true exported CL/test JSONL and compare with original Unity Legacy Input on same signed game candidate. If failure, fix expected vs observed with recorded traceback before claiming success.
- INPUT-005 OPEN; LOCAL-005 remains open for non-regression. NOT_READY 0/3.
