# T4 — authentic Raft 1.1.01 mouse button and wheel call-site routing

**8 November 2026 | INPUT-005 | source-only | no Unity player/device proof**

## Why this test exists
The owner observed that physical mouse movement rotates the Raft camera under Android Pointer Capture, but LEFT/RIGHT/MIDDLE clicks and both wheel directions do not operate inside the game. The T4 capture listener source has read-only bounded native action observability (commit `b89ccb9b`, source CI42510026195); it does not synthesize Unity input. Android View captured pointer dispatch is a separate callback route from normal generic motion, so a listener returning false is **not** independent proof that Unity Legacy Input received an event.

## Immutable source and experiment
- Original ZIP2 Raft managed assembly: `Raft/Raft_Data/Managed/Assembly-CSharp.dll` from commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, exact size **3,211,776 B**, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- Scanner `scripts/t4_original_button_wheel_routing.py`, isolated synthetic controls `tests/test_t4_original_button_wheel_routing.py`, workflow `.github/workflows/raft-t4-original-button-wheel-routing.yml`.
- [CI42512688990](https://github.com/alwansan/raf/actions/runs/42512688990) **SUCCESS**: 6 source-free tests; authenticated exact DLL; pinned ILSpy11.2.0.10050 private decompile; **2,395** C# files scanned. Nothing private uploaded; Actions output contains only aggregate numeric counts.

| Lexical interface in original compiled-assembly decompilation | Count |
|---|---:|
| `Input.GetMouseButtonDown` | 4 |
| `Input.GetMouseButton` | 6 |
| `Input.GetMouseButtonUp` | 2 |
| `Input.GetAxis[Raw]("Mouse ScrollWheel")` | 6 |
| `Input.mouseScrollDelta` | 2 |
| `MyInput.GetMouseButtonDown/GetMouseButton/GetMouseButtonUp` | 0 |
| `MyInput.GetAxis[Raw]("Mouse ScrollWheel")` | 0 |
| Direct `Mouse.current.{left,right,middle}Button` | 0 |
| Direct `Mouse.current.scroll` | 0 |
| Calls with non-literal `GetMouseButton*(argument)` | 1 |

**Interpretation:** 12 original direct Legacy button calls and eight Legacy scroll references are present as source syntax, including one dynamic button index. This is **not a runtime call graph** or evidence that these sites are exercised in a particular gameplay scene. The private C# decompiler may normalize aliases, symbols or branch structures; other DLLs and indirect wrappers are not included.

## Decision tree for safe repair
1. Install/use the one existing shared Mini APK (artifact from [42509945996](https://github.com/alwansan/raf/actions/runs/42509945996), not a new T4 APK). Collect physical mouse cases T4-01..09, including capture ON/OFF, all three buttons, vertical/horizontal scroll and keyboard/camera preservation. Verify actual media export and the source SHA; do not infer PASS from merely returning to the app.
2. When a fresh signed full Raft test candidate actually includes the T4 capture listener `b89ccb9b` and its exact source SHA, compare its `physical_mouse_captured_action_callbacks` and `physical_mouse_relative` logs with actual owner actions. Old 42058825739 can verify world/save/reopen only for its old binary; it contains none of these later callbacks.
3. If physical captured actions do not arrive, investigate Android focused View/callback delivery (not game method patches). If native captured actions arrive but original `Input.GetMouseButton*` / scroll remain false, implement a fail-closed Android-only targeted legacy shim for exactly those authenticated source sites with no double event dispatch; preserve original Windows fallback and touch virtual LEFT/Mouse0.
4. Require identity and old source byte checks, expected site cardinality 4/6/2 buttons and 6/2 scroll, strict C# and Unity2021 Android+Editor compilation, and a real device proof on the same signed APK candidate. Do not alter Unity input globally or force mouse state without proving Unity receives no equivalent event.
5. Full Unity/OBB/XAPK build uses separate existing 5/5 trial policy or explicit owner direct request; shared mini build policy is different. Do not modify native requests, cancel teammates, or declare READY.

## Current boundaries
The source census and its regression are complete; the physical device callback/Legacy input gap is **not repaired or verified**. INPUT-005 stays OPEN; game readiness remains NOT_READY 0/3. No source of Raft compiled DLL, scene, shader, save, or proprietary content was published.
