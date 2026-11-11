# T4 INPUT-005 — live source/device evidence audit
session_id: 20261111T1940Z-T4-scheduled-live-audit-q8m3
origin: scheduled
base_sha: e90f4c4dab5dfbc16aa4ee58d0fcbe0c952fb872
branch: feature/android-native-port
scope: evidence-only; no shared Unity/Android input files, no T5 display or mini lab writes
experiment_key: T4-INPUT-005-captured-versus-reader-device-identity
resource: GitHub metadata and existing pinned CL read-only; no Unity build

## Verified
- Owner phone artifact 42058825739 (source e9c358ed) created, entered, saved and reopened world; package publication failed separately. Preserve original .rgd and LOCAL-005 regression evidence.
- Owner 5 Nov report includes black Android cursor/system bars; T4 owns physical mouse capture and in-game Raft cursor transitions. T5 owns Resolution and right-side diagnostic controls.
- Prior pinned CL/test 8 Nov has 373 deduplicated physical mouse events, 13 left press/release and 55 vertical scroll, but all captured=false; no capture-on/game reader evidence. Right/middle/horizontal not proven attempted.
- Prior original ZIP2 adapter source CI42518143297 success for 20 Unity Legacy button/wheel call sites; this is source validation, not device confirmation.
- Latest queried Actions list (20 entries) includes CI43084365164 T1 success, CI43081428467 T5 Settings delegate success and CI43074969451 runner guard success; no current physical mouse device result or game build shown. This first-page list is not an exhaustive absence proof.
- Current classifier is aggregate-only and explicitly cannot establish event causality. No safe gameplay code change justified from uncaptured-only evidence.

## Acceptance and next action
Use a single identified APK/build SHA, Android PID and monotonic capture epoch: requestPointerCapture ON -> captured=true real mouse LEFT/RIGHT/MIDDLE down/up, vertical/horizontal scroll -> corresponding frame-latched Unity original reader and visible Raft action. Check camera, focus release, keyboard, Settings and old .rgd regression. A failed step must be localized before modifying JNI or Unity routing. Coordinate one unified mini capture-ON trial with T5, not duplicate Unity XAPK/CI. No claimed phone validation, game remains NOT_READY.
