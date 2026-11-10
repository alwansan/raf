# T4 session 20261110T0939Z-T4-scheduled-gate-source-audit-r6m2
origin: scheduled
start HEAD: 6b31f9779bab9964ed1f37291c44b4aa367e6ac2
work-plan commit: a9a247bb2e212d6afa166808f58d9a56fb3c9cf8
scope: INPUT-005 Android physical mouse capture eligibility audit

Read owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM CHAT_AND_SCHEDULE/PROMPT/OPERATING_MODEL, T4 MEMORY and prior CI context. Owner-confirmed world enter/save/exit/reopen from run 42058825739 remains valid; package publication failure is distinct. No fresh device trial was performed.

## Evidence
Current production file android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs blob 99b3926bf5f3352c0e38aad858eb834be39472a8: PhysicalMousePresent loops InputSystem Mouse.all; Update() computes shouldCapture=!paused && focused && authoredLocked && physicalPresent. Consequently requestPointerCapture cannot be requested when physicalPresent=false even if Android InputDevice recognizes a physical mouse. This is a precise *potential* failure boundary, not proof of the observed click/scroll defect. Diagnostic physical_mouse_capture_eligibility was added previously; do not mistake source CI 42776921454 SUCCESS for a phone pass. Source-only audit; no behavioral change or CI rerun.

## Resume
Inspect a fresh signed-game JSONL: compare authoredLock, focused, paused, inputSystemPhysicalMouse and shouldCapture to capture-request/probe and physical button/wheel callbacks. If Unity registration false while Android physical mouse connected, add an Android-only bounded capability probe (not a blanket mousePresent bypass) and run unit+managed compile; preserve virtual touch exclusion, keyboard, legacy fallback, and release on focus loss. Coordinate T5-owned resolution/UI separately. No duplicate full build. INPUT-005 OPEN; LOCAL-005 remains OPEN with owner artifact world/save evidence.

Work: prompt/coordination/clients/T4/work/20261110T0939Z-T4-scheduled-gate-source-audit-r6m2.md
