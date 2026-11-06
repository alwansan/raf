# T4 → T5: first Unity error preserved across logger initialization recovery

- author: T4; session: `20261106T1719Z-T4-chat-first-unity-error-recovery-b5q7`; origin=chat.
- issue: LOCAL-005 remains OPEN, full game NOT_READY 0/3.
- native delivery: **no** T4 Unity/APK/OBB build requested, dispatched or cancelled.
- exact source fix: `5e0b52a8e9aef6bf0f66e54a51bc890f3151c20b`; final source CI test SHA `af9e5c5c4192cf5f2df776ca860ae0731347f49f`.

Before this fix, `AndroidRuntimeLog.UnityMessage` grouped the first Unity critical exception even when `sink==null` after failed logger startup; its `Write` was a no-op. After retrying initialization and restoring storage, the same exception was silently discarded as an already-seen duplicate and no original full stack was persisted. Actual original source is compiled under synthetic UnityEngine API as source-only `.NET8` tests.

- [Red CI42260446981](https://github.com/alwansan/raf/actions/runs/42260446981) failed **check291** at `Program.cs:258` after successful source compile and initial storage-error controls.
- [Production fix 5e0b52a8](https://github.com/alwansan/raf/commit/5e0b52a8e9aef6bf0f66e54a51bc890f3151c20b) defers group/dedup until a sink actually exists, while returning **true** without sink so the bounded in-game HUD can still capture errors.
- [Final CI42260791146](https://github.com/alwansan/raf/actions/runs/42260791146) completed **SUCCESS 297/297**, original first full Error record and legitimate repeat_summary counted **separately**; offline platform source CI42260791155 also SUCCESS. Intermediate [CI42260590793](https://github.com/alwansan/raf/actions/runs/42260590793) had only a test assertion that counted summary text as duplicate; test-only [af9e5c5c](https://github.com/alwansan/raf/commit/af9e5c5c4192cf5f2df776ca860ae0731347f49f) fixed that.
- [Technical report](../../../../docs/T4_FIRST_UNITY_ERROR_AFTER_LOGGER_RECOVERY_2026-11-06.md) and [T4 session](../../clients/T4/sessions/20261106T1719Z-T4-chat-first-unity-error-recovery-b5q7.md).

Use the next single **source-attested signed APK+matching OBB** already coordinated by T5 for actual device validation: verify package/versionCode, installed APK/OBB checksums, `logger.ready`, persisted first `operation=Error` with full stack, and genuine world creation/save/force-stop/reopen. Synthetic storage-unavailable scenario is **not** evidence the owner's physical storage failed. Owner old build [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) still OWNER_CONFIRMED for world-save-reopen at older source. T4 did not touch water/FFT, shaders, OBB, T5 Resolution/three buttons, Settings, audio, touch/virtual controller or mouse capture. T4 scheduled continues mouse provenance independently; no duplicate native CI.
