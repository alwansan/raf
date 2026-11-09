# T4 scheduled session 20261109T1044Z-T4-scheduled-capture-request-observability-v2q9

origin: scheduled

track: INPUT-005 OPEN

base_HEAD: bbce0ed66026db03eda86fea3d34383968e3a063

source_commits: ee6d17c2, 4191a2a7, 0890514f, 14d52fea

work: ../work/20261109T1044Z-T4-scheduled-capture-request-observability-v2q9.md

## Restoration

Owner DEVICE_FEEDBACK_42058825739_AR.md: Artifact 42058825739 entered local world, saved, exited, reentered on owner phone. Original .rgd compatibility preserved. CL 8 Nov uncaptured left/wheel evidence only; no captured click/scroll phone proof. T4 20 original Legacy Input sites source integration CI42518143297 succeeded but not device verified. Previous scheduled T4 20261109T0951Z CL review found no captured events in inspected exports.

## Implementation

scripts/t4_analyze_mouse_lab_routes.py previously discarded capture_request ON/OFF; now reports attempt counts and request without confirmed callback. This does NOT claim capture grant. Four regression cases added scripts/tests/test_t4_capture_request_observability.py: request-only, confirmed callback, OFF/invalid request, uncaptured wheel after request. No Unity, keyboard, save, Settings, sound or T5 display files edited.

## Evidence and limits

Latest checked HEAD bbce0ed6; T2 CI42600762796 successful. New Python tests NOT EXECUTED; container GitHub DNS resolution failed. No redundant CI or APK launched. INPUT-005 OPEN, NOT_READY 0/3.

## Next

Execute Python unit tests; obtain actual T4 capture_request ON, captured=true route and LEFT/RIGHT/MIDDLE/V/H wheel from phone; compare with Unity Legacy counters in same signed game; coordinate T5 single mini build. No claim game mouse fixed.