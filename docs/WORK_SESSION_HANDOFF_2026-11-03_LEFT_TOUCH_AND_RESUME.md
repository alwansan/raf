# Owner correction, permanent resume and recovery helper — 3 November 2026

Read [current owner requirements](CURRENT_OWNER_REQUIREMENTS.md), `AGENTS.md` and [prompt/STATUS.md](../prompt/STATUS.md) first. They supersede older contradictory instructions.

## Reviewed evidence

Read the supplied `الجلسة2.txt` completely: its final checkpoint is source`f4df907d3c017810cf758a5e280ad68ea54a2e1b`, matching live GitHub before this work. `الجلسة1.txt` was not available to the session and has not been read. Reviewed the current DirectX handoff, relevant latest device/FFT findings, source/CI workflows and current touch code. Original source probe41545664983 succeeded. No Unity/APK was started by this session.

Original evidence and open graphics/audio/world limits remain in [the DirectX handoff](WORK_SESSION_HANDOFF_2026-11-03_DIRECTX_TO_WORK.md) and [FFT inventory report](ORIGINAL_WATER_LFS_COMPUTE_INVENTORY_2026-11-03.md). Do not replace original field/index dataflow with guessed math or equate translated shader validation with phone correctness.

## Owner's correction: LEFT touch

The earlier request for right-click was a wording mistake. Current touch outside interactive UI synthesizes **left mouse / Mouse0**, retains one-update short-click pulses and500ms held drag until release/cancel/pause/focus loss. Original UGUI and controller/editor surfaces retain touch ownership; physical right mouse remains physical input.

Renamed authored identifiers and files: `AndroidRightTouchPointer`→`AndroidTouchPointer`, `RightTouchGesture`→`TouchPointerGesture`, `RightTouchButtons`→`TouchPointerButtons`, with neutral command names and test directory `Tests/TouchPointer`. Updated runtime bootstrap, original MyInput alias, candidate source staging, full-workflow source list and cheap-CI triggers. **No full-workflow dispatch or request JSON change.** Original assets and GUIDs unchanged; these authored runtime types are dynamically added, not original serialized game types.

`Input.simulateMouseWithTouches` remainsfalse in original startup and authored pointer: enabling it would create automatic left-click duplication in addition to the explicit pointer and interfere with controller touches. The explicit left path is covered by source assertions and an actual-method C# harness verifying left button output, Mouse0 merging, untouched physical right/other keys, release and absent-device behavior. Pure gesture/pulse timing tests remain. Actual InputSystem/Unity/phone behavior is still unverified.

Older historical RIGHT/Mouse1 descriptions in the prior append-only history are labelled superseded at each affected document's top; they describe previous code/commits and must not be followed as current requirements. Historical CI results are not rewritten as tests of this correction.

## Permanent session transfer

The owner no longer needs to request a handoff message each time. `prompt/CONTINUE_RAFT_AR.md` is the stable ready-to-copy message; `prompt/STATUS.md` links the current evidence and next step; `prompt/README.md` explains their use. `AGENTS.md` requires future sessions and repair tasks to update these after meaningful results and before ending a session.

## Additional scheduled work

The latest owner message authorizes **one additional recovery/research automation** without Unity/APK production. Keep the existing hourly task unchanged. The extra task must perform independent bounded source/resource fixes and CPU-only experiments, avoid duplicate concurrent work, inspect HEAD and use expected-SHA writes, preserve branch/source constraints, and update the permanent prompt/status. Its actual creation result and schedule will be recorded after the scheduler confirms success. A recurring task runs in scheduled cycles; it is not continuous execution between runs.

## Validation

At preparation:14 touch policy,8 offline startup and11 render/audio/source checks passed locally. Additional mapping/gesture C# execution and original managed compatibility compile pending automatic cheap CI. Build hold remains active. Follow results and update this handoff and prompt/STATUS.md; do not ask for a fresh APK test to proceed with independent engineering.
