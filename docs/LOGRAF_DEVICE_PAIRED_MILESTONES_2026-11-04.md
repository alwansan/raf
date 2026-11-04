# LogRaft 0.6.86 device evidence and milestones — 2026-11-04

**Writable branch:** `lograf` only. Read-only game HEAD at review: `6b60c35e845a3bc8e559a7df7e408363032697cb`. Inputs were private owner-supplied ZIPs; **no raw user logs or app-private profile data are committed**.

## Evidence from the Poco F5 Pro / Android 15

The user-supplied `LogRaft-1793819191475.zip` is **LogRaft 0.6.86**, captured 22:00:53–22:06:29 Asia/Baghdad. The completed session summary reports:

- 2,205,648 observed game-UID Logcat lines; seven raw segments, 222,255,712 recorded bytes; 7,134 accepted and 7,134 written batches, zero local failed batches, 99 ms worst writer queue delay, 131,261 bytes peak queue, no reported Logcat reconnection.
- One owner issue marker was both enqueued and written, showing `timestamp_unix_ms` and `elapsed_realtime_ms` in the raw log. This verifies writer operation in this session, not guaranteed physical-flash persistence or absence of upstream Android Logcat losses.
- 99 of 104 samples had readable SurfaceFlinger presentation FPS (mean **42.77** among readable samples; **not** Unity Update FPS). All 102 game-running telemetry rows had readable Android `dumpsys meminfo` PSS. Shell GPU clock and per-process I/O remained unavailable and null.
- Final counters: **79,432** `UltimateWater` invalid shader passes, **12,700** `water_fft_invalid_compute_kernel`, **9,949** cursor RGBA32 warnings, and two `obb_guid_load_failed` (patch expansion path). An absent optional patch OBB cannot, by itself, establish corruption of the installed main OBB. No game process-death event was observed; the game remained alive at Stop.

A second owner ZIP contains **game-private** `raft-logs` sessions at 18:08 and 19:00 UTC, including Unity frame timings, scene transitions and FMOD bank diagnostics. Game-internal FMOD probes recorded successful MasterBank bank loading (**533** events) and successful other bank loads, but those private messages were **not all emitted to Logcat**. This external recorder cannot assume permission to read another app's sandbox. Audio output itself was not verified.

The game-private second session observed MainScene loading, `InternalAddPlayer`, `SaveWorld.exit exceptionEscaped=False`, and the externally available Logcat contained `World has been loaded`. None alone establishes playable offline input or correct water rendering; the original-shader/water/FFT failures persist.

## Engineering change: fixed-vocabulary milestone summary

Logcat already carries a handful of events that are buried among ~2.2 million raw lines. A new bounded, low-allocation `GameMilestoneSummary` tracks **only the logged presence** of:
- `RAFT_FMOD_ANDROID_BOOTSTRAP`
- `RAFT_ANDROID_DEVICE_TEST`
- `Raft_Network:OnSceneLoaded`
- `Raft_Network:InternalAddPlayer`
- `World has been loaded`

These are included in 3-second metrics as `game_milestones` and final session summary as `final_game_milestones`, so events at the end of a recording are not lost between metric samples. The first/last times are **local observation wall times**, not exact Unity execution times; the original logcat event timestamps remain untouched in raw files. Logged callbacks, banners and bootstrap strings are not interpreted as operation success.

This adds no user-data upload, Shizuku permissions, private-file reads or expensive log rescanning. Existing no-delete segment policy, capped binder/SAF queue, verified main PID, null unavailable FPS/GPU/memory metrics and permanent signing identity are unchanged.

## Validation required

Run recorder v0.6 safety invariants and actual JVM regression tests (positive/negative milestone fixtures and reset) in the existing GitHub Actions signed APK workflow. Only a new Poco F5 Pro run can verify in-device latency, marker counts and `final_game_milestones` after installation of the next version. CI success is **not** phone success, nor a Raft game repair.
