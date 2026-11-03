# A7 — independent INPUT-005 recovery

- Session: A7-20261103T100214Z-4121ce131222; client: raft-20261103T100214Z-c83d58d4; UTC 2026-11-03T10:02:14Z; base SHA `cb95d4bb8b736013f996a7583e434775a5160223`.
- Goal: investigate LEFT Mouse0 Android touch ownership / cancellation / held drag without modifying original UGUI/controller/physical-input semantics; source-only bounded experiment.
- Read: `prompt/README.md`, `prompt/CONTINUE_RAFT_AR.md`, `prompt/STATUS.md`, `docs/CURRENT_OWNER_REQUIREMENTS.md`, `AGENTS.md`, `prompt/coordination/README.md`, latest linked handoff; recent HEAD/Actions/releases and CL log tree (read-only).
- Other coordination reviewed: FFT-FORMAT-009 independent completed/paused, DISPLAY-003 active, HAPTICS-008 two active agents. No touch-work client was listed at registration. Avoid those paths; recheck live work before writing.
- No queued/in-progress branch Actions at initial review. No Unity/APK/OBB/XAPK, release or scheduled-task requests authorized for this role.
- Hypothesis pending source inspection, not a claimed defect. Last phone APK80 precedes new left-input fixes; CPU tests are not phone proof.
- Next: inspect live pointer files and test harness; plan a precise regression, run local checks, update own experiment and handoff if verified.

## Verified A7 final checkpoint — 2026-11-03

- Added `BoundaryMatrix.cs` plus `Program.cs` test call in [source caa9bb7ae76da9920d46b4474d3fc2c10e994e1a](https://github.com/alwansan/raf/commit/caa9bb7ae76da9920d46b4474d3fc2c10e994e1a); no production runtime, original assets or .meta/GUID change.
- [Platform CI41616691487](https://github.com/alwansan/raf/actions/runs/41616691487), job125851777246: **COMPLETED SUCCESS**. Actual C# `RAFT_TOUCH_POINTER_GESTURE checks=425 holdMilliseconds=500 passed=true actualUnityDeviceExecution=false`. Mapping harness `checks=53 syntheticButton=left legacyKey=Mouse0 physicalDevicesPreserved=true actualUnityDeviceExecution=false`.
- Cases:499/500/501ms, four clock origins, cancelled tap/hold, secondary-finger nonownership,128 rapid pulses alternating press/release. No actual phone runtime or original rendering restoration claim.
- Existing owners for DISPLAY-003, HAPTICS-008, FFT and local-world were not overwritten. No Unity/APK/OBB/XAPK/release/automation/native request, and no CL modification.
- INPUT-005 bounded *test* work completed only; overall game remains NOT_READY, no candidate/0-of-3 full reviews. Future work must start with fresh coordination read.
