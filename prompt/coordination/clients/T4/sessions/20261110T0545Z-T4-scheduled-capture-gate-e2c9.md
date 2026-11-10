# T4 checkpoint — 20261110T0545Z-T4-scheduled-capture-gate-e2c9
origin: scheduled
session_id: 20261110T0545Z-T4-scheduled-capture-gate-e2c9
resumed_from_sessions: 20261110T0439Z-T4-scheduled-device-presence-g5k2; 20261110T0336Z-T4-scheduled-capture-retry-audit-j6p9
issue_id: INPUT-005
scope_commit: 028417c824c1e188f2619c9c465903a5adc9dfd9
source_commit: be31b5532a842544bf48a7ad744c5081d21cbd8c
work: prompt/coordination/work/T4/20261110T0545Z-T4-scheduled-capture-gate-e2c9.md
origin_report: docs/DEVICE_FEEDBACK_42058825739_AR.md

## Actual change
Read original owner report first: phone owner confirmed entering, saving, exiting and reopening world only on artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628, while package publication failed. This remains an artifact-specific OWNER_CONFIRMED LOCAL-005 success, not a later candidate claim. Existing 8 Nov authentic original game source has 20 Legacy mouse button/wheel call-site adapters, but gameplay LEFT/RIGHT/MIDDLE/wheel remains unverified.

Reviewed AndroidPhysicalMouseCapture.cs: Update() requires authoredLock && PhysicalMousePresent() && focus && !pause. Android View pointer capture cannot be requested if Unity InputSystem Mouse.all does not register a physical mouse. This is a hypothesis, not a device-confirmed fault. Added bounded state-transition marker `physical_mouse_capture_eligibility` with paused/focused/authoredLock/inputSystemPhysicalMouse/shouldCapture and explicit androidCaptureGranted=unknown. Does not bypass safety gate, alter capture state, keyboard, touch, cursor, UI, .rgd, audio or Settings. No device identifiers or per-frame logging.

## Verification and limits
Source edit was exact-anchor checked against the current GitHub file and GitHub content-SHA conditional update succeeded. No Unity compilation, CI, Android device test, CL new upload, or gameplay mouse acceptance performed in this run. Do not call SOURCE_VERIFIED or DEVICE_CONFIRMED from this source-only commit. No Actions canceled or repeated. Existing CL/test mini data captured=false cannot establish game behavior.

## Next
Check source compile/policy CI already running before dispatch. In a signed full game build containing source_commit, compare eligibility marker with authored_lock, capture_requested/retry, captured callbacks, legacy reader evidence, and actual LEFT/RIGHT/MIDDLE/wheel game effects. If authoredLock=true but inputSystemPhysicalMouse=false with real Android mouse connected, investigate registration/device-source independent gate safely without triggering capture from virtual LEFT touch. Preserve keyboard and old .rgd world save/reopen. Coordinate with T5 for full game and Resolution; no duplicate build. INPUT-005 OPEN; LOCAL-005 regression pending.
