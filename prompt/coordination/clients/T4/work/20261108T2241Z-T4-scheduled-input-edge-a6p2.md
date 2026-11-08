# T4 INPUT-005 independent work scope
session_id: 20261108T2241Z-T4-scheduled-input-edge-a6p2
origin: scheduled
base_head: 7e1861f502b8d4ed2bbf7bffab6b4bd376c6c075
scope: source-only physical mouse button edge ambiguity audit, no runtime change
experiment_key: T4-INPUT005-ACTION_DOWN-actionButton-zero
files: this unique work file and matching unique session only
shared_resource: none; NO_BUILD; T5 owns shared Mini and Resolution/UI buttons
hypothesis: Android ACTION_DOWN/ACTION_UP can carry actionButton=0; treating those as explicit button edges may miss left click; inferring from buttonState alone risks false positives and duplicate route delivery. Need capture ON/OFF evidence before runtime change.
protected: keyboard, touch Mouse0, original .rgd/world/save, audio, Settings, camera pointer capture.
owner evidence: 42058825739 world/save/reopen SUCCESS; newer owner game camera moves, buttons/wheel not working; original game source adapter 20 call sites/12 files CI42518143297 PASS but not device proven.
acceptance: physical SOURCE_MOUSE captured=true with capture epoch and DOWN/UP/BUTTON_PRESS/RELEASE for left/right/middle and SCROLL V/H, then compare Unity legacy consumers; fail closed on missing evidence.
