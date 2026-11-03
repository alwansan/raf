# A7 INPUT-005 secondary-touch packet routing

Identity `raft-20261103T132738Z-a7f64e28`, session A7-20261103T132738Z-c42b078e; resumed_from completed previous A7 `raft-20261103T121120Z-a7b60d42`. Start 2026-11-03T13:28:17.119Z.

Read live permanent owner prompts, STATUS, AGENTS, coordination templates, latest handoff/readiness; fresh HEAD, Actions (no running/queued at initial check), older APK80 source, read-only CL log root; peer HAPTICS/WATER/FFT/RENDER/DISPLAY/LOCAL work. Prior INPUT-005 A7 scopes all completed, no overlap with AndroidTouchPointer source or intended new harness.

Public Unity InputSystem 1.7 exact tag `Unity-Technologies/InputSystem:1.7.0`, `Packages/com.unity.inputsystem/InputSystem/Devices/Touchscreen.cs`, reviewed. Its `GetStateOffsetForEvent` restricts TouchState control reads to primaryTouch, and primary remains first finger until last release. Unity 1.7 public `StateEvent.GetState<TouchState>(InputEventPtr)` reads raw individual per-touch state without unsafe or custom layout, see https://docs.unity.cn/Packages/com.unity.inputsystem@1.7/api/UnityEngine.InputSystem.LowLevel.StateEvent.html.

Likely source issue: UGUI/gamepad first finger primary; secondary gameplay finger raw TouchState ignored/misrouted by authored `AndroidTouchPointer.OnEvent` using only `primaryTouch.*.ReadValueFromEvent`. Plan: source-extracted actual C# OnEvent harness with stricter event doubles, fail first then minimal production fix to select raw TouchState, fallback to old full-snapshot event decoding where needed; ensure sticky UI ownership, Mouse0, physical devices untouched. CPU harness is NOT real Unity/Android execution. Do not build Unity/APK/OBB/XAPK or alter native request/tasks/protected branches/CL.
