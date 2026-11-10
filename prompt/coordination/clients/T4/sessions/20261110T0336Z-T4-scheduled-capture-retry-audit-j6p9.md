# T4 checkpoint — 20261110T0336Z-T4-scheduled-capture-retry-audit-j6p9
origin: scheduled
session_id: 20261110T0336Z-T4-scheduled-capture-retry-audit-j6p9
resumed_from_sessions: 20261110T0235Z-T4-scheduled-evidence-gap-n7q4; 20261109T2042Z-T4-chat-release-final-window-q6n4
base_sha: 887d74f3a53fc00c70de1a179c0097d19119ed4b
scope_commit: 2196f3e05c94d513d6337aa2afd7a4edc3b23baa
work: ../work/20261110T0336Z-T4-scheduled-capture-retry-audit-j6p9.md

## Evidence preserved
Owner's signed artifact 42058825739 (source e9c358ed) successfully entered a local world, saved .rgd, exited and reopened on POCO F5 Pro. Packaging publish failed, so this is artifact-scoped phone evidence, not new-build certification. Report docs/DEVICE_FEEDBACK_42058825739_AR.md and CL immutable 520c4cf are the sources. Later shared CL test T4-01..09 remained NEEDS_INPUT as of preceding session.

## Concrete source inspection this run
Read current android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs, including CapturedListener, TryCapturedFrame, Update, ProbeCapturedPointer and RequestCapture. Non-MOVE captured callbacks record authentic button/scroll events, return false to original View handling; the Legacy wrapper supplements only when native is silent and requested/nativeCaptured are true. On probe, different focused View identity clears captured state, and the next Update attempts a fresh request after nextRequestTime. Therefore **the alleged permanent view-change deadlock is not established by source**. No speculative patch is warranted. A different possibility remains: Android never delivers a captured callback on the focused Unity View; only signed-game logs can distinguish this from missing Legacy reads. Existing mini trace captured=false and capture requests=0 is not signed-game proof.

## CI / status
Live HEAD at start 887d74f3a53fc00c70de1a179c0097d19119ed4b; latest inspected completed workflow 42747722414 SUCCESS is T1 FFT and does not validate T4. No new Unity build launched. No game code changed, no CI duplicated. INPUT-005 OPEN, LOCAL-005 OPEN for remaining regressions, full game NOT_READY. T5 retains Resolution and right-side HUD buttons.

## Next executable step
Obtain new signed-game JSONL with physical_mouse_capture_requested/retry, capture view changed/lost, physical_mouse_captured_action_callbacks, physical_mouse_legacy_reader_evidence and final release outcome for one uninterrupted epoch. Distinguish missing request, denied View capture, callback absent, getter absent, and gameplay unresponsive before changing the bridge. Compare keyboard and save/reopen on same signed build. If no phone evidence, inspect a separate source-level boundary rather than repeat this audit.

## Limitations
No device execution or new APK; no claim that LEFT/RIGHT/MIDDLE or wheel works in Raft. The source audit rejects one hypothetical failure, not INPUT-005 as a whole.
