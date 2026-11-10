# T4 INPUT-005 scoped investigation
session_id: 20261110T0439Z-T4-scheduled-device-presence-g5k2
origin: scheduled
baseline_sha: 671f2ca3177df94b88b23808bca78c5715a08f24
status: source-audit / device evidence blocked

## Scope and hypothesis
Read-only inspection of android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs and CL/test inventory. Specific hypothesis: PhysicalMousePresent() gates requestPointerCapture on InputSystem Mouse.all registration; on Android a physically connected mouse may generate Android MotionEvent but fail this InputSystem enumeration. If so request count remains zero even though physical mouse moves. This is **not proven** by current owner CL tests, which recorded uncaptured callbacks only. No change to shared T5 Resolution or UI, original save .rgd, keyboard, touch, audio or Settings. No CI resource reserved.

## Experiment key
INPUT-005/T4/device-presence-g5k2: in a signed Raft build correlate mouse device discovery (Mouse.all), original authored cursor lock intent, and physical_mouse_capture_requested for the same epoch. Existing mini callbacks are not sufficient. Do not remove physical-device gate or capture on touchscreen without device proof.

## Evidence
Owner artifact 42058825739 successfully created/saved/reopened local world; publish step failed; docs/DEVICE_FEEDBACK_42058825739_AR.md. Existing 20261110T0336Z T4 session already excluded a permanent view-change deadlock from code. Latest CL/test directory observed shared-20261109-233132-554663211; T4-01..09 NEEDS_INPUT in prior review. Last inspected Actions 42747722414 SUCCESS concerns T1 FFT, not mouse.

## Next step
Use signed-game JSONL with lock intent, capture request and physical mouse presence; if lock intent exists but request absent, test Mouse.all device enumeration. If requests exist, inspect view identity/hasPointerCapture and then getter evidence. INPUT-005 OPEN. No phone/Unity run or source fix claimed.
