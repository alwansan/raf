# T4 isolated work — 20261110T1240Z-T4-scheduled-mouse-evidence-v9k3
origin: scheduled
baseline_sha: a1184a61eb2f4fb33e83f1527ab5310fbb287009
issue: INPUT-005 OPEN / LOCAL-005 OPEN
experiment_key: T4-INPUT005-native-vs-legacy-20261110T1240Z
shared_resource: none; no Unity build, no lab APK, no workflow dispatch
scope: documentation-only device evidence decision protocol; no modification to T5 Resolution, unified mini APK, AndroidPhysicalMouseCapture.cs, .rgd, Settings or keyboard

## Verified starting evidence
Owner phone 2026-11-05 run 42058825739 successfully entered, saved, exited and reopened a world. Packaging publishing failed, not the world scenario. Original game source run e9c358eda01785b65e4eb14f18723da426635628; no claim about newer signed packages. Source currently contains captured callback, fallback and getter counters; no signed Raft device proof of LEFT/RIGHT/MIDDLE/scroll. T4 source-only classifier CI 42776921454 passed earlier. CL/test newest shared directory is shared-20261109-233132-554663211; T4-01..09 NEEDS_INPUT as last verified. CL main latest b3286b326d73ee511cd2f68a43c92a1233c2f8d1 dated 2026-11-09 20:37:44Z, with no newer test directory observed.

## Single decisive experiment — real signed Raft gameplay, not mini lab
Record signed APK SHA, versionCode, OBB SHA, run ID, device model, input device ID and scene (menu vs local world). Start with keyboard navigation and Escape sanity checks; preserve Android back/exit. In menu: test authored cursor and system cursor visibility. In world: lock cursor, rotate beyond display edges, then LEFT/RIGHT/MIDDLE press/release and vertical/horizontal wheel, followed by Escape, focus loss and USB/Bluetooth disconnect/reconnect. Pair timestamped input logs with action observed in gameplay; do not equate callback count or getter count with success.

## Decision criteria
A: authoredLock=false or focus=false => no capture request expected; preserve original behavior.
B: native Android SOURCE_MOUSE verified but physicalPresent=false => eligible device discovery mismatch, inspect InputDevice source and reject touchscreen/virtual touch.
C: physicalPresent=true and request attempted but hasPointerCapture=false => inspect View identity, window focus and retry epoch.
D: capture observed + authentic action callbacks, buffered=0 => classification/frame staging fault; inspect event time/deviceId/actionButton/buttonState and frame.
E: buffered>0, getterCalls=0 => original game consumer not patched/called in this scene. getterCalls>0, positiveFallback=0 => frame sample ordering; positiveFallback>0 but no gameplay action => cursor/UI ownership or action binding.
F: click passes but black system cursor or Android bars persist => separate cursor/WindowInsets bug, coordinate with T5 safe-area and Resolution without modifying their files.

## Source invariant / next engineering action
Never consume non-move captured pointer callbacks solely to simulate click: listener currently returns false to preserve Unity original route. Preserve original Input.GetMouseButton* / GetAxis and keyboard first, native captured fallback only when capture provenance is verified. Next cycle: inspect any newer CL game trace for first failing boundary, then implement smallest source fix with source test and CI, only if trace distinguishes B/C/D/E/F. If no new trace, build a source-only controlled regression for the most plausible frame-order boundary without claiming device success.
status: evidence_plan_ready; no gameplay fix claimed.
