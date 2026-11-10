# GFX-LAB — 20261110-GFX-chat-auto-logs-export-04

- session_id: `20261110-GFX-chat-auto-logs-export-04`; origin: `chat`; resumed_from: `20261110-GFX-chat-material-delta-03`
- base_sha: `a134108fac5f59e503aab388969abbb9720b2e66`
- source SHA: `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- status: `IMPLEMENTING`
- user destination: `/storage/emulated/0/Download/Games/cl/test/g/`

## Scope and acceptance
After user 16 photos/13 COPY LOG lacked individual channel and sampling changes, implement automatic per-state snapshots and every Unity log including full stack traces. Store all historical sessions in app persistentDataPath and compress into ZIP with one button. Android >=29 scoped MediaStore.Downloads sets RELATIVE_PATH=Download/Games/cl/test/g/. On failure keep private ZIP, show error (no fake external export success). No Android root/unsafe MANAGE_EXTERNAL_STORAGE permission. Signed Android Unity2021.3 GLES3 APK to be built separately in GFX-LAB branch.

## Negative controls
Original Shader48 shader NOT restored; Standard/ChannelProbe diagnostic only. Original source private inside GitHub runner. No T-Team/production branch edits. Device owner must independently confirm external ZIP path and file contents after installing resulting APK; Unity compile and emulator cannot guarantee actual MIUI filesystem behavior. Continue deeper Shader48 source investigations as independent scope, closure gates in gfxlab/SHADER48_MODEL_PHASE_CLOSURE_AR.md.

## Runs and results
Pending.

## GFX-MULTI-031 — Automatic all-test logs + ZIP to requested Downloads (2026-11-10)
- User requested automatic per-test model/mode/role/RGB/R/G/B/A/Source-vs-Linear/surface snapshots, full Unity errors/stack traces, all sessions compressed by one button to `/storage/emulated/0/Download/Games/cl/test/g/`.
- Added `gfxlab/unity/Assets/Scripts/GfxSessionRecorder.cs`: per app launch append-only `sessions/<UTC>-<ID>/events.jsonl`, `snapshots.jsonl`, `summary.json`, timestamp/frame/sequence, every user state change and periodic 15-second snapshot; all Unity messages/error stacks via threaded callback + queue, disk failures & dropped-record counter; flush on pause/focus loss/quit.
- Added `GfxDownloadsZipExporter.cs`: ALL historical private app sessions and last report into ZIP, CRC-entry read validation, excludes prior export ZIPs to avoid recursive growth; original Shader48 still false. Added `Assets/Plugins/Android/GfxDownloadsBridge.java`: API29+ scoped `MediaStore.Downloads` `RELATIVE_PATH=Download/Games/cl/test/g/`, IS_PENDING transaction and post-publish RELATIVE_PATH/SIZE checks; no broad storage permission/root. On any failure show `EXPORT FAILED`, retain ZIP in private `persistentDataPath/gfxlab/exports/`.
- Updated six-model viewer to `GFX-MULTI-031`: auto state on selection, material, channel, role, sampling, surface, camera/controls, 15s heartbeat; `EXPORT ZIP` plus optional old `COPY LOG`; status visible. Builder embeds recorder and publishes separate package `com.alwansan.raft.graphicslab.autologs`, version 0.5.0, Unity 2021.3.45f2 Android GLES3 ARM64, six authenticated original meshes/21 image links. **No original Shader48 restored**.
- `gfxlab/tools/auto_log_zip_audit.py`+tests ingest future owner ZIP automatically; count multi-session state matrix, warnings/exceptions/stack presence, missed records and file errors without public log contents. [CI42801864098](https://github.com/alwansan/raf/actions/runs/42801864098) SUCCESS parser source-free regression.
- Initial APK CI [42800909094](https://github.com/alwansan/raf/actions/runs/42800909094) & [42800994512](https://github.com/alwansan/raf/actions/runs/42800994512) FAIL during source-free tests: old channel package ID assertions and permission-token commentary test; fixed. Next APK CI [42801247423](https://github.com/alwansan/raf/actions/runs/42801247423) progressed to Unity but FAIL C# compiler ambiguous `CompressionLevel` (`UnityEngine` vs `System.IO.Compression`), fixed with qualified .NET enum. Source/private ZIP2 purged on every failure.
- **CURRENT APK run [42802005319](https://github.com/alwansan/raf/actions/runs/42802005319) IN PROGRESS**, SHA `e4498b71320f96d6df8a75ea090620ec88a9a8bd`. Verify real Unity compilation, Gradle/Java plugin, signed APK/package/artifact, purge before release. Source-only CI does NOT prove MediaStore physical path on MIUI; owner must press EXPORT and check ZIP in requested folder on phone.
- Full instructions `gfxlab/ANDROID_AUTO_LOG_EXPORT_AR.md`. Original Shader48, per-pass resources/CB semantics, actual PC↔Adreno pixels, rig/animation and model family closure all remain BLOCKED; defer separate worker until source/pixel gates proven.

## GFX-MULTI-031 signed APK proof (2026-11-10)
- [GitHub Actions 42802005319](https://github.com/alwansan/raf/actions/runs/42802005319) **COMPLETED SUCCESS** at immutable source build SHA `e4498b71320f96d6df8a75ea090620ec88a9a8bd`. Real Unity2021.3.45f2 Android IL2CPP ARM64 GLES3 BuildPlayer succeeded with 6 authentic original models / 7 Renderer Material slots / 21 original Texture2D roles privately staged from original ZIP2 SHA and purged afterward.
- **191 source-free unit tests passed**, verified exactly one APK with AndroidManifest.xml, classes.dex, libunity.so ARM64, APK CRC, `apksigner verify`, and `aapt` package name `com.alwansan.raft.graphicslab.autologs`; artifact upload + all private source purge passed.
- `GfxLab-Multi-Six-AutoLogs.apk` exactly **66,162,049 bytes**, SHA256 `a2466155b87d8c34ec22955a22bc6c7c741f691063e9a9f7f79a58ca9465c1f5`. [APK Artifact 13757546087](https://github.com/alwansan/raf/actions/runs/42802005319/artifacts/13757546087) expires **2026-11-17T11:02:53Z UTC** (artifact ZIP 66,166,513 bytes).
- [Automated ZIP parser CI42801864098](https://github.com/alwansan/raf/actions/runs/42801864098) SUCCESS, 191 tests; safe parser `gfxlab/tools/auto_log_zip_audit.py` will process user-exported ZIP in next chat without manually copied per-test clipboard reports.
- A supplementary source-free [signed APK Java DEX check 42804520804](https://github.com/alwansan/raf/actions/runs/42804520804) is running to confirm `GfxDownloadsBridge` and exact `Download/Games/cl/test/g/` string inside compiled APK. **Do not claim owner MediaStore path successfully written yet; requires device test.**
- `originalShaderRestored=false`, `originalAnimationRestored=false`, `actual_android_original_shader48_pixel_parity=false`; original source Shader48 pass states/register/CB and PC parity remain OPEN. The current APK still uses Unity Standard and diagnostic ChannelProbe. This deployment only solves per-test logging workflow, not true source Shader48 restoration.
