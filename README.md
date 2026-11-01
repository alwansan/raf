# LogRaft — dedicated Raft Android diagnostic recorder

Standalone Android app for **Raft v1.1.01 Android Native** device testing.
This source lives **only** on branch `lograf` of `alwansan/raf`. It is not the game APK and includes no game binaries/assets.

## Target and purpose
- Target Android package: `com.alwansan.raft.androidtest`.
- Unity 2021.3 / ARM64 IL2CPP / FMOD; POCO F5 Pro (Android 15).
- Preserve Unity, Java, native, Audio/FM​​OD, Adreno/EGL/Vulkan, input, ActivityManager/ANR logs **when actually published into Android Logcat**.
- Start recording *before* launching Raft; continue in a user-initiated foreground service across game termination.
- Shizuku UserService reads Logcat as shell/root, instead of relying on an ordinary app's restricted background READ_LOGS access.
- One full game-UID stream across main, system, crash and events buffers; **separate** Raft-related system context lines from system/crash/events. No unrelated application log dumping to disk by default.
- Output: choose a base folder via Android Storage Access Framework. Each capture creates `LogRaft-<timestamp>/session-info.txt`, `raft-*.log` segments, **32 MiB per segment with no delete-on-rotation**. When stopped, **Share** creates ZIP inside the session folder.
- Recording only stops on explicit Stop, service/permission/process death, storage failure, device shutdown, or external OS enforcement. Shizuku must remain available.

## Phone steps
1. Install and start [Shizuku](https://shizuku.rikka.app/). Android 11+ wireless debugging works without a PC; root is optional. It normally must be restarted after phone reboot.
2. Install `LogRaft-debug.apk` from [GitHub Releases](https://github.com/alwansan/raf/releases), filter tags starting with `lograf-`. Android may warn about sideloading.
3. Open LogRaft and select a writable user-owned **folder**. Do not select another app's inaccessible `Android/data` directory.
4. Grant Shizuku permission to LogRaft. Allow notifications and set battery usage to unrestricted if available.
5. Tap **Start** then **Open Raft** and reproduce the issue; leave LogRaft running with its notification in the background.
6. Return, tap **Stop**, then **Create ZIP and Share**. ZIP is also saved in the chosen session folder. Verify its contents before uploading publicly.
7. Send session's ZIP privately, or review/redact and upload to a suitable diagnostics folder. Logs can include identifiers or sensitive paths.

## Coverage and important limits
There is no universal "record absolutely everything" Android API. Logcat only includes published log messages, not every game function call, scene frame, input action, GPU command, or filesystem operation. Log buffers can roll over and the OS can kill even foreground services; a shell UID may see less than root on some vendor devices. No unlimited disk storage exists. The app **never silently deletes older log segments**, but stops and reports writes when its SAF provider fails or the device fills up.

The game has its **own** `Application.persistentDataPath/raft-logs` JSONL diagnostics within `Android/data/com.alwansan.raft.androidtest/files/`. Android scoped storage usually blocks another unprivileged app reading that location. These Unity diagnostics complement LogRaft, and developers should preserve first-failure events. See the latest game branch checkpoint `docs/WORK_SESSION_HANDOFF_2026-11-01_DEVICE_RENDER_INPUT_PERFORMANCE.md`.

This version monitors **one fixed package** intentionally; it does not request QUERY_ALL_PACKAGES. ADB/shell is used only by the Shizuku remote reader. Raw data is not uploaded to any server.

## Design references
- [Android logcat documentation](https://developer.android.com/tools/logcat) — buffers, UID filter, metadata formats.
- [Android logging restrictions](https://source.android.com/docs/core/tests/debug/understanding-logging) — background READ_LOGS limits.
- [Shizuku-API](https://github.com/RikkaApps/Shizuku-API) — Binder and UserService model.
- [LogFox](https://github.com/F0x1d/LogFox) and [ShizuLog](https://github.com/opfans432/ShizuLog) — compared feature sets **only**, code not copied.

## Build
JDK 17, Android SDK 35, Gradle 8.9, Android Gradle Plugin 8.7.3.

```bash
gradle --no-daemon :app:assembleDebug
```

GitHub Action `.github/workflows/lograf-apk.yml` on the **lograf** branch builds and publishes `LogRaft-debug.apk` as a standalone GitHub prerelease. It needs no game build, Unity, license, LFS checkout or PC.

## Test acceptance checklist (on actual Poco F5 Pro)
- [ ] Shizuku permission dialog works, can bind service, and app reports target UID.
- [ ] LogRaft records **while Raft is in foreground**; notification remains visible.
- [ ] A known `Unity` console error appears in saved game log.
- [ ] Raft force-close and native crash are recorded and LogRaft keeps running.
- [ ] System context lines reference Raft, not unrelated apps.
- [ ] Continuous 30+ min session grows across segment rollover; no old segment deletion.
- [ ] Stopping closes files; ZIP has all segments and metadata.
- [ ] Storage revoked/full gracefully indicates failure.
- [ ] Reboot/Shizuku shutdown does not falsely claim capture continued.
- [ ] Android device battery optimization doesn't evict the foreground collector in regular tests.

**CI compilation is not hardware evidence.** Never label a build device-verified until those checks pass.
