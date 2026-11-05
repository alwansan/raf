# LogRaft 0.6.88 — Nov 5 device ANR, lifecycle responsiveness repair

**Scope:** ONLY the writable `lograf` branch in `alwansan/raf`. The owner supplied three LogRaft session ZIPs / LF sub-sessions and an Android ActivityManager ANR report for Poco F5 Pro, Android 15 (API 35). Raw private logs, filenames inside app-private directories and device IDs are **not** committed.

## Confirmed phone observations

- The Android 15 system report explicitly records `ANR in com.alwansan.lograf (com.alwansan.lograf/.MainActivity)` around **2026-11-05 22:13:30 local**, PID 14291, with `Input dispatching timed out`, **5,000ms** wait for `MotionEvent(action=HOVER_MOVE)`. It contains system CPU/memory-pressure information but **no captured Java main-thread stack** identifying the exact blocking method. This is an ANR, not proof of an uncaught Java crash, shader failure, or that all data was lost.
- A short incomplete LogRaft capture started around 22:13:18 (the `lf.zip` subset), near that incident. It lacks a completed `session-summary.json`. Android can kill services after a serious ANR; no logger can guarantee final flush on force-kill.
- Two completed 0.6.88 exports **did** save complete session summaries: 22:01 session **6,878/6,878** accepted/written batches, zero local failed batches, one accepted/written owner marker, 141ms max queue lag; 22:09 session **2,234/2,234**, zero local failed batches. This is *local writer* evidence, not proof the OS Logcat ring never lost lines.
- In the earlier completed session: **76,592** water-invalid-pass roots (Spectrum 30,075, Foam 46,517), **11,627** invalid FFT kernel roots, 133 telemetry samples with only **3** readable SurfaceFlinger FPS measurements. In the later session: **23,884** water-invalid-pass roots (Spectrum 8,484, Foam 15,400), **3,850** invalid kernel roots; 57 readable SurfaceFlinger FPS samples of 71. These are separate game-side failures, not evidence the logger itself introduced shader defects.
- The existing `MainActivity` refresh ran every **1,100ms** even when the UI was hidden behind the fullscreen game, repeatedly parsing large JSON, rebuilding/selecting a long TextView and reflowing it. In `CaptureService.onStartCommand` the code synchronously called `DocumentsContract.createDocument`, `ContentResolver.openOutputStream`, queried Shizuku and wrote metadata before returning; `ServiceConnection.onServiceConnected` invoked a remote Binder `start` on Android's main thread. Any of these can delay input response under device IO/CPU pressure, but the missing main-thread stack **prevents selecting one as proven sole cause**.

## Engineering repairs on lograf

1. **Serialized service control worker:** The main thread immediately calls `startForeground(...)` as required, then queues `initializeSession(recovering)` to a single lifecycle executor. SAF directory/file creation, metadata writes, Shizuku readiness queries and bind request no longer run synchronously in `onStartCommand`.
2. **Binder startup off main:** `onServiceConnected` schedules package UID resolution and `IRemoteLog.start` on that same control executor, checks active/stopping/failed states, and ignores late callbacks after executor shutdown without reviving a stopped session.
3. **Stop and destruction off main:** User STOP enqueues `halt`, remote stop, 18-second maximum writer drain, close, and summary persist on the same worker. `onDestroy` never calls `halt` synchronously; startup/stop FIFO is honored. Fatal-stop uses the control worker instead of spawning separate unsynchronized stopper threads.
4. **Background UI updates disabled:** MainActivity refresh is active only in `onStart`..`onStop`, with a 3,000ms cadence approximately matching the 3-second telemetry sample. Opening fullscreen Raft stops background TextView re-layout.
5. **Measured startup latency:** The session summary exposes `session_startup_phase` and a nullable `session_remote_startup_duration_ms` (monotonic elapsed from foreground-service request to confirmed Binder `start` reply). A missing reply stays null, never reported as successful.

## Invariants and test plan

Preserve the `com.alwansan.lograf` package/signing identity, Shizuku permissions, 512-batch/12MiB bounded queue, 32MiB raw segments, original raw Logcat, user markers, .zip exports, metric null semantics and writer flush logic. Existing Python safety checks now assert the service's main-thread command cannot perform SAF document creation, the Binder start is background, STOP/Destroy never join the SAF writer on Android main, late callbacks cannot restart after shutdown and UI refresh stops when hidden. Existing JVM diagnostics and synthetic 17,178-event FFT replay still run. CI must pass compile/sign/release, but **Poco F5 Pro verification is required** with game running, app visible, repeated STOP/START, and Shizuku disconnect to confirm ANR is no longer reproducible.

No game, CP/CL repo, original asset or scheduled automation is modified.

## Verified CI and distribution

- Code commit: [`6c921211678adae6b0b122a6f6bef8f1004252a0`](https://github.com/alwansan/raf/commit/6c921211678adae6b0b122a6f6bef8f1004252a0).
- GitHub Actions: [run **42098272069**](https://github.com/alwansan/raf/actions/runs/42098272069), **COMPLETED SUCCESS**, head exactly that commit. Structural checks passed the new serial executor, off-main SAF, off-main Binder start, off-main destruction, and background UI refresh guards. The existing actual JVM diagnostic regression also passed, including its 17,178-event synthetic FFT stress replay. Android release Gradle reported **BUILD SUCCESSFUL in 53s**.
- Test-signing certificate comparison passed with SHA-256 `bdb27cfad1fd9a6ac14bd47317206ce4df462040f45ddb1fdbb66a0974043149`. This is the **certificate fingerprint**, not the APK file hash. Original signing p12 and package identity remain unchanged.
- Published [signed LogRaft 0.6.89](https://github.com/alwansan/raf/releases/tag/lograf-89): `LogRaft-signed.apk` **167,932 bytes**, automatic `versionCode=1089`, `applicationId=com.alwansan.lograf`, plus matching SHA-256 sidecar.
- **On-device ANR resolution remains unverified** until Poco F5 Pro 0.6.89 test. Source changes mitigate identified blocking paths but the owner-supplied ActivityManager ANR report contained no main-thread Java trace, so it is not valid to claim a specific root cause was proven or that the ANR is definitively gone.
