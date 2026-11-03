# A3 — Vendor ShaderLab restoration transaction recovery

4 November 2026 (UTC checkpoint 2026-11-03T23:14Z). Agent A3, new coordination client `raft-20261103T230700Z-a3e8b74f`, session `a3-20261103T230700Z-c64da0f2`, resumed from completed `raft-20261103T224800Z-a3c41e7b`. Writable branch: `feature/android-native-port` only.

## Concrete defect and RED evidence

The shared production `scripts/restore_tmp_shaders.restore` services authenticated TextMesh Pro 3.0.6, PostProcessing v1, and VolumetricLights shader restoration. Before the fix, an I/O failure halfway through restoring original shaders left newly written vendor includes/fallbacks/LICENSE in the Unity project, even when the original shader files rolled back. A failure while creating external backups could strand an incomplete backup; symlinked Assets/RaftAndroid directory parents redirected new shader files outside the project. Partial source staging may interfere with later real Unity shader import, though it does not establish device rendering failure.

Synthetic [RED test commit 8316f5b8](https://github.com/alwansan/raf/commit/8316f5b8b8d4e913dd309af30ba4342f0f980af0) ran the **real shared restorer**, not a duplicate. [CI41737057615](https://github.com/alwansan/raf/actions/runs/41737057615), job126268842611, FAILED as intended: four broken scenarios, one normal PASS, synthetic vendor shader data only.

## Fix and GREEN CI

[Source ab556f12](https://github.com/alwansan/raf/commit/ab556f12d398e91b58fa6ed395d71ac6af2f1024) implements fail-closed per-path symlink/containment checks before copying or writing vendor sources; preflights output conflicts and keeps byte-identical existing dependencies; copies original .shader and .meta bytes into an exclusively created external backup with cleanup on incomplete backup; creates new includes/fallbacks/notices exclusively with `open('xb')`; on failure restores changed original shader bytes and removes only newly created additions; on incomplete rollback reports an error and retains the full external backup. Original GUIDs are never rewritten or regenerated.

[GREEN CI41737411435](https://github.com/alwansan/raf/actions/runs/41737411435), job126270048884, completed **SUCCESS** on exact fix SHA: **5/5** new A3 synthetic transaction tests, **4/4** previous TMP, **3/3** PostFX, **6/6** Volumetric — **18/18**.

## Limits and coordination

This repairs the **restoration pipeline**, not original custom UltimateWater shader authenticity or Android GPU results. Original ZIP2 assets, shader binaries, texture colour, material bindings and .meta/GUID files were not modified; no LFS, Unity build/import, native APK/OBB/XAPK/Release or phone test. VolumetricLights additionally writes a separate BSD notice *after* the shared restore function; that caller-specific operation is not covered by this scoped transaction. Malicious concurrent filesystem changes and host power loss remain outside the CPU tests.

W1's built-in shader restorer, A1's FFT work, W2/W3 material maps and all other agents' source files were left untouched. Global **WATER-001**, **RENDER-002**, **FFT-FORMAT-009** remain OPEN; build **NOT_READY**, no immutable candidate and full reviews **0/3**. A3 scope completed; on continuation recheck live HEAD/Actions and use a new session identity.
