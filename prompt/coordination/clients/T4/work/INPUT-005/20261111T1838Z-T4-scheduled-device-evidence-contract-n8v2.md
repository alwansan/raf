# T4 INPUT-005 — device evidence contract
session_id: 20261111T1838Z-T4-scheduled-n8v2
origin: scheduled
baseline_sha: f97adef519118a904b481bd01edbe92b13673a97
status: active
scope: T4-only device evidence validation, no T5 UI/Resolution files, no shared mini APK edits
experiment_key: INPUT-005/captured-to-legacy/20261111T1838Z-n8v2
shared_resource: none; no Unity or Actions launch

## Verified baseline
Owner 5 Nov artifact 42058825739: world enter/save/exit/reopen worked on phone, delivery publishing failed; source e9c358eda01785b65e4eb14f18723da426635628. Do not conflate with later game source. 8 Nov T4 authentic CL evidence at 4680f5dc: 373 unique uncaptured Android mouse events, 13 LEFT press/release pairs and 55 VSCROLL; no captured=true evidence. Existing source-only 20 legacy call-site bridge CI42518143297 succeeded but not device-confirmed. T4 classifiers are diagnostic, not a gameplay fix.

## Independent investigation / falsifiable evidence gate
A captured mouse action can only be diagnosed after capture_request=ON and route=captured on the same process/build and chronological window. For LEFT/RIGHT/MIDDLE require button press and release with consistent buttonState/actionButton and subsequent original Unity consumer evidence; for wheel require signed vertical/horizontal axis and original reader trace. Preserve keyboard typing/focus, Android back/exit, touch Mouse0, menu cursor visibility and relative camera capture. If native callback is absent, investigate Android View ownership and focus before changing legacy consumers. If callback exists but reader absent, investigate frame-latch and source staging before changing Android capture. If both exist, test actual gameplay action; aggregate counter correlation alone is not success. No additional source patch without real causal evidence.

## Non-overlap / acceptance
T5 owns moving Show Xbox/Xbox layout/Test report and existing Settings Resolution. T4 owns physical pointer capture and Raft cursor transition. No source edits or new build this checkpoint; existing T4 source adapter must first be tested in a signed game containing it, not older artifact 42058825739. T5 shared Mini is single-build policy; do not duplicate. Preserve original .rgd, .meta GUID, audio, Settings. INPUT-005 OPEN; LOCAL-005 phone world success is version-scoped; NOT_READY 0/3.

## Next action
Use CL logs of one capture-on session with build SHA and PID to classify callback vs original reader, then patch only the demonstrated gap. If no such evidence, add narrow capture-on regression in unified testpack via T5's coordinated scope, not another standalone APK.
