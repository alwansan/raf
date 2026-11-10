# T4 INPUT-005 scope — 20261110T0939Z-T4-scheduled-gate-source-audit-r6m2
origin=scheduled; baseline_head=6b31f9779bab9964ed1f37291c44b4aa367e6ac2; owner device evidence=42058825739 (world create/save/reopen confirmed only on that artifact).

## Independent hypothesis and exact boundary
The current AndroidPhysicalMouseCapture.cs PhysicalMousePresent() enumerates only Unity InputSystem Mouse.all and excludes RaftAndroidTouchLeft. Update() requires this boolean to call RequestCapture(). Android may deliver physical mouse MotionEvents even when Unity InputSystem has not registered a Mouse. That is an unproven but concrete capture-start gate. The existing 2026-11-10 eligibility log can distinguish authoredLock/focus/paused/inputSystemPhysicalMouse; successful CI 42776921454 is source-only and does not prove hardware.

## Files/resources and conflict
Read-only audit of android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs, no production edit; this work file and independent session file only. Do not modify T5 Resolution, touch, keyboard, .rgd, audio, Settings, shared CI or native build requests. No Unity job launched. Physical device confirmation requires signed game trace showing physical_mouse_capture_eligibility and capture request/captured events. If physicalPresent=false while authoredLock=true and Android mouse is present, implement a bounded Android InputDevice capability probe with explicit virtual/touch exclusion, then C# source test and real device trial; do not remove the gate blindly.

## Outcome
Source audit confirms an exact conditional dependency, not a proven defect. Preserve existing source-only CI pass 42776921454 and owner world/save/reopen success. INPUT-005 OPEN, no phone button/wheel verification. Next: inspect newest signed game JSONL with this eligibility marker and coordinate one test with T5; only then change gate behavior.
