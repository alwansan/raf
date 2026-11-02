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

## New in v0.2.0 — game performance telemetry
- Every ~3 seconds: game process CPU (% of one core and normalized across device cores), RSS and peak RSS, threads, per-process I/O counters, and system memory.
- Less frequently: process PSS, battery level/temperature, thermal status, Qualcomm Adreno KGSL GPU busy and frequency where readable.
- Best-effort SurfaceFlinger SurfaceView presented FPS estimate, NOT Unity's actual Update FPS. Android 15 may deny or omit this metric.
- Missing or blocked readings are null, never fake zeros.
- Separate metrics-*.jsonl segments (8 MiB), preserved along with the original full raft-*.log (32 MiB) segments.
- Live metrics in the app, plus a Mark issue action both in the app and notification for correlating a glitch to performance samples.
- The existing game branch has its own internal AndroidTestDiagnostics frame and Unity memory counters in its private sandbox; this independent logger cannot assume access.
## November 2, 2026 — measured device session

An owner-supplied LogRaft v0.5.34 recording from Poco F5 Pro (Android 15) began at 19:19:22 local time and included:
- 1,008,422 raw log lines and 33 samples across around 104 seconds.
- 38,744 invalid Graphics.Blit pass messages, 1,430 invalid compute-kernel messages, and 35 missing-path exception lines for packaged Android haptics assets.
- Raft game PID 21258 died at 19:20:58 while foreground. am_proc_died identifies process death, **not why**. No Fatal signal, SIGSEGV, FATAL EXCEPTION, or ANR was found in these recorded segments.
- Available device memory fell to roughly 604 MB. Peak process RSS was approximately 1.63 GB and process CPU reached ~265% of one core. Correlation with shader errors is not proof of causation.
- SurfaceFlinger FPS reported in 14/33 samples, approximately 3.9–120.7 presented frames/s. This is **not Unity game FPS** or GPU frame time. GPU busy was readable, while GPU clock was unavailable.

The follow-up version adds in-stream cumulative error counters (shader passes, compute kernels, missing asset paths, Java/native fatal markers, and process deaths), live status labels, and an automatically exported session-summary.json containing last telemetry and recorder totals. Raw log segments are retained without filtering or deletion.
## New in v0.6 — recorder backpressure, frame telemetry quality and session statistics

- Raw Logcat and metrics now arrive into a **bounded FIFO** on Binder callbacks, and a separate slightly low-priority SAF writer handles actual file writes. Logcat's remote reader is not blocked by every SAF flush. Hard limits: 512 pending batches and 12 MiB pending bytes.
- **On queue overflow or SAF write failure, recording stops with an explicit incomplete-data warning**, rather than silently discarding records. This does not prove Android's own rotating Logcat buffers cannot lose lines; such losses remain unknown.
- Stop lets the remote reader deliver its last batches, then drains the writer queue before closing files and building `session-summary.json`. Stop runs off the UI thread.
- `session-summary.json` now reports local writer received/written/failed batches, queue peak size and worst delay, plus per-session observed min, max, mean and valid-sample counts for FPS, CPU, RSS, PSS, GPU, battery temperature and Logcat throughput.
- Frame tracking now reports *why* presented FPS is missing: unavailable surface, insufficient frames, layer baseline, stale timestamps, SurfaceFlinger failure, or invalid estimate. Missing SurfaceFlinger data is **not** reported as 0 FPS or confirmed Unity freeze. A separate `FRAME_TELEMETRY_STALE` warning marks observations that stopped progressing.
- PSS exposes a candidate value and a quality marker (`validated_estimate`, `rejected_pss_exceeds_rss`, `unavailable`); rejected values are not presented as reliable game memory.
- User-reported CPU/GPU/RAM figures on Poco F5 Pro remain best-effort external indicators. For authoritative per-frame Unity CPU/GPU timings, the game itself must emit them.

## Suggested validation on the Poco F5 Pro

1. Install the latest `LogRaft-signed.apk` over the prior stable-signed Build 42 without clearing app data or existing recording folders.
2. Start Shizuku and LogRaft, choose a writable local SAF destination, start capture, then open Raft.
3. Run one short baseline and one high-error-water/Shader-heavy session. Add a user marker shortly before a visible problem, wait a few seconds and stop using the notification or app.
4. Check the ZIP includes all `raft-*.log`, `metrics-*.jsonl`, and `session-summary.json`. Inspect `writer_failed_batches`, `writer_peak_pending_bytes`, `writer_max_queue_delay_ms`, and `performance_statistics`.
5. Check `fps_tracking_status`, `frame_telemetry_stale` and `process_pss_quality`. Do not conclude the game froze solely because FPS became unavailable.
## Phone steps
1. Install and start [Shizuku](https://shizuku.rikka.app/). Android 11+ wireless debugging works without a PC; root is optional. It normally must be restarted after phone reboot.
2. Install `LogRaft-signed.apk` from [GitHub Releases](https://github.com/alwansan/raf/releases), filter tags starting with `lograf-`. Android may warn about sideloading.
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

## One-time permanent signing (automatic)

No Termux commands or GitHub Secrets are required. GitHub Actions has generated and committed the public **test** signing key to `signing/lograf-public-test.p12`. Every future release uses that exact key. Each GitHub Actions build increments `versionCode` automatically and publishes a verified signed APK named `LogRaft-signed.apk`. Read [signing/README.md](signing/README.md) for the certificate fingerprint and limitations of using a public signing identity.

Older `LogRaft-debug.apk` releases were signed with unrelated debug keys, so switching from these to the stable signed APK might require a **one-time uninstall**. Back up existing recorded sessions first; no uninstall should be necessary between future stable-signed releases.

## Build
JDK 17, Android SDK 35, Gradle 8.9, Android Gradle Plugin 8.7.3.

```bash
gradle --no-daemon :app:assembleDebug
```

GitHub Action `.github/workflows/lograf-apk.yml` on the **lograf** branch builds and publishes `LogRaft-signed.apk` as a standalone GitHub prerelease. It needs no game build, Unity, license, LFS checkout or PC.

## Test acceptance checklist (on actual Poco F5 Pro)
- [ ] Shizuku permission dialog works, can bind service, and app reports target UID.
- [ ] LogRaft records **while Raft is in foreground**; notification remains visible.
- [ ] A known `Unity` console error appears in saved game log.
- [ ] Raft force-close and native crash are recorded and LogRaft keeps running.
- [ ] System context lines reference Raft, not unrelated apps.
- [ ] Continuous 30+ min session grows across segment rollover; no old segment deletion.
- [ ] metrics-*.jsonl is parseable with 3-second timestamps and nulls for unavailable metrics.
- [ ] Compare CPU/RSS to independent system readings; KGSL utilization is device-wide, not game-only.
- [ ] Mark issue button/notification records a matching timestamp.
- [ ] Stopping closes files; ZIP has all segments and metadata.
- [ ] Storage revoked/full gracefully indicates failure.
- [ ] Reboot/Shizuku shutdown does not falsely claim capture continued.
- [ ] Android device battery optimization doesn't evict the foreground collector in regular tests.

**CI compilation is not hardware evidence.** Never label a build device-verified until those checks pass.


See [2026-11-01 17:30 device findings](docs/DEVICE_LOGS_2026-11-01_173033.md).
