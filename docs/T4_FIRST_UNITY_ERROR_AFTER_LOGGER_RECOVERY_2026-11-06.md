# T4 — original Unity first exception after Android logger storage recovery (6 Nov 2026)

- **Owner:** T4, session `20261106T1719Z-T4-chat-first-unity-error-recovery-b5q7`, `origin=chat`.
- **Issue:** `LOCAL-005` remains OPEN; original world/save mechanism unchanged.
- **Production source commit:** [5e0b52a8e9aef6bf0f66e54a51bc890f3151c20b](https://github.com/alwansan/raf/commit/5e0b52a8e9aef6bf0f66e54a51bc890f3151c20b).
- **Exact source-free red CI:** [42260446981](https://github.com/alwansan/raf/actions/runs/42260446981) completed FAILURE at `Program.cs:258`, `check=291`, not a compile error.
- **Final source-free green CI:** [42260791146](https://github.com/alwansan/raf/actions/runs/42260791146) completed SUCCESS source `af9e5c5c4192cf5f2df776ca860ae0731347f49f`, `RAFT_PERSISTENT_LOG_TEST checks=297 passed=true actualAndroidStorageVerified=false`.
- **No native Unity/APK/OBB build, private original game inputs, or owner-phone validation** was performed in this session.

## Authenticated implementation / negative control

The production `AndroidRuntimeLog.UnityMessage(type, detail, critical)` formerly called `RepeatedDiagnosticMessages.First` before checking whether its persistent `sink` existed. If the Android application sandbox directory failed at initialization, `sink==null` but `UnityMessage("Error", original full stack, true)` still marked the error as seen, while `Write` performed no disk write. After the earlier T4 startup-retry fix allowed recovery of `AndroidRuntimeLog.Initialize`, the same original exception was suppressed as a duplicate **without having ever stored a full stack**.

This was validated using the **real** conditionally compiled `AndroidRuntimeLog.cs` under `UNITY_ANDROID` and synthetic `UnityEngineStubs.cs`, not a copied reimplementation. A deterministic test creates a regular file where `Application.persistentDataPath` should be a directory, requiring initial `StorageError`. While sink is absent, the real `UnityMessage("Error", "synthetic first exception\nSyntheticStackTrace_T4", true)` must return `true` for `AndroidTestDiagnostics` HUD. The fixture replaces the obstructing file with a directory, retries the real logger, calls that exact error again, and requires `true` (first **durable** occurrence), followed by `false` on its third occurrence. The final actual JSONL must contain exactly one full `operation=Error` entry with original stack and one separate `operation=repeat_summary` entry after `Shutdown`. Existing startup, flush, rotation, failed-storage, concurrency and JSONL tests remain active.

On old source, [CI42260446981](https://github.com/alwansan/raf/actions/runs/42260446981) failed **at the recovered error return assertion** (`check291`), after actual source C# compile and initial assertions passed. Minimal production [fix 5e0b52a8](https://github.com/alwansan/raf/commit/5e0b52a8e9aef6bf0f66e54a51bc890f3151c20b) handles `sink == null` **before** dedup grouping, returning `true` to preserve original in-game HUD behavior. With a real sink, unchanged grouping and critical durable writes continue.

The first post-fix [CI42260590793](https://github.com/alwansan/raf/actions/runs/42260590793) advanced past the formerly failing assertion but failed `check295` when the test incorrectly counted the intentionally emitted `repeat_summary` (which reproduces the original text) as a duplicate full crash. Test-only [af9e5c5c](https://github.com/alwansan/raf/commit/af9e5c5c4192cf5f2df776ca860ae0731347f49f) refined the assertion to distinguish `"operation":"Error"` from `"operation":"repeat_summary"`; both are required, neither hidden. Final [CI42260791146](https://github.com/alwansan/raf/actions/runs/42260791146) passed 297 checks.

## Limits / Android delivery

This is **not evidence that the owner's storage was unavailable**, only an actual source defect demonstrated by injection. This bounded fix does not address the separate question of a `sink` that exists but suffers a write failure after startup. The owner's [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), immutable source `e9c358eda01785b65e4eb14f18723da426635628`, remains separately OWNER_CONFIRMED for world enter/save/exit/reopen. None of these source-only tests proves newest signed Unity APK, physical mouse, original .rgd durability, water/FFT/color recovery, main OBB mount or device graphics.

T5 can include source `5e0b52a8` or descendant in a future single signed package and verify actual device-generated diagnostics and original SaveWorld/SaveUser/reopen markers on the **same** installed source/OBB identity. Do not produce a duplicate native build for this source-only fix. Keep `LOCAL-005` and `INPUT-005` OPEN, full game readiness NOT_READY 0/3.
