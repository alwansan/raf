# T4 INPUT-005 evidence and non-duplicate scope
session_id: 20261111T2037Z-T4-scheduled-mouse-proof-c7r9
origin: scheduled
branch: feature/android-native-port
observed_recent_commit: 9b89f62772c2c61f6269fd2249f8560af1522892 (repository-wide search; not independently verified branch HEAD)
status: evidence_review_only; waiting_device_proof

## Scope / hypothesis
Read owner phone feedback, shared lab feedback, T4 MEMORY/state, last scheduled session and current classifier/tests. The immutable phone success of run 42058825739 (world/save/reopen) is retained, while source CI42518143297 only validates 20 authentic original Legacy Input call-site adaptations, not physical mouse behavior in the game. Device CL evidence pinned 4680f5dc from 8 Nov records 373 unique uncaptured Android mouse events, including 13 LEFT press/release pairs and 55 vertical scroll events; no captured=true route, no right/middle/horizontal attempts proven. Source adaptation and test classifier already exist; do not duplicate.

## Experiment key and shared resources
INPUT-005/physical-capture-game-consumer-pair; no shared Unity/CI resource requested. File ownership: this new work file and session only. T5 retains shared mini APK, resolution and on-screen controls; T4 owns physical pointer capture and game input consumption.

## Critical next proof
Use the same signed full-game build and process: record APK/OBB manifest and commit, pointer capture request/accepted/released epochs, Android source/device/buttonState/actionButton and V/H scroll, frame-indexed Unity fallback latch and original Raft consumer reads for LEFT/RIGHT/MIDDLE and scroll. Test physical left/right/middle press and release and wheel both axes with capture ON, then capture OFF negative control, focus loss and reacquire, keyboard unchanged, save/reopen regression. Distinguish Android callback -> bridge -> Legacy reader -> gameplay action; aggregate growth alone is not event causality. If captured callbacks occur without corresponding game reads, patch the demonstrated bridge/reader boundary only.

No game source edits or CI started: no new device captured=true evidence and source-only fixes already validated; launching duplicate tests would not close the missing proof. Preserve .rgd, .meta, GUID, audio, Settings and touch. LOCAL-005 phone scenario PASS only for run 42058825739; INPUT-005 OPEN, NOT_READY 0/3.
