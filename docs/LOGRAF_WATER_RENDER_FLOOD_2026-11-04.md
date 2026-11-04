# LogRaft material-level water and shader-error flood diagnostics — 2026-11-04

**Branch:** `lograf` only. Paired owner-supplied private ZIPs: LogRaft `0.6.86` and Raft's game-private `raft-logs` on Poco F5 Pro / Android 15. No raw private archives, profile details, shader source, or paths are committed.

## Measured evidence (22:00:53–22:06:29 Asia/Baghdad)

The complete raw session recorded **79,432** `Invalid pass number` root lines. Exact fixed-material classification, derived by scanning those lines without inference:

| Water material | Invalid-pass lines |
|---|---:|
| `UltimateWater/Spectrum/Water Spectrum` | **35,346** |
| `UltimateWater/Foam/Global` | **24,912** |
| `UltimateWater/Utilities/Blur (Subsurface Scattering)` | **12,700** |
| `UltimateWater/Utility/Noise` | **6,474** |
| **Total** | **79,432** |

The session also contained **12,700** `Invalid kernelIndex (6)` roots. LogRaft's existing stack-correlated error classifier attributed these to water FFT; raw index 6 alone is not proof of the stack origin. Game-private logs show original Unity graphics state and a water/compute problem persisting despite Vulkan/Adreno and some successful game initialization.

Over approximately **334 seconds**, there were roughly **276 shader/compute error roots per second**. The earlier generic `error_flood_warning` only flagged Logcat rates of 10,000 *all lines* per second; that conflates log line volume with the actual persistent renderer error rate.

## Recorder improvements

- A bounded, zero-path-retention `RenderFailureSummary` class counts fixed categories for Spectrum, Foam, Subsurface Blur, Noise and other UltimateWater invalid-pass roots, plus numeric compute index-6 vs other roots. This avoids expensive offline scanning of millions of raw lines for the next test.
- Emit `render_failure_breakdown` in 3-second metrics and `final_render_failure_breakdown` in the stop-time session summary. The original `ultimate_water_invalid_pass` error group and all untouched raw lines remain available. Counts are per matching Logcat root line, not unique shader assets.
- Emit `render_error_roots_per_second` and an explicitly heuristic `render_error_flood_warning` for **100+ shader-pass plus invalid-compute root messages per second** during a completed sample interval. The warning is **not** a GPU hang, shader compiler failure, OS crash or memory leak diagnosis. Keep missing first-interval rates absent, never zero.
- Surface the rate/warning in the existing UI and include `render_error_flood_warning_samples` plus rate statistics in the session-level metrics summary. No remote frame profiling, private game file access, new permission, or automatic upload is added.
- JVM regression fixtures test exactly the four observed materials, unknown/bystander material negative controls, repeated index-6 roots, interval threshold and non-finite rate rejection. Existing diagnostic and signing checks still run through the established Actions workflow.

## Acceptance and limits

CI must pass structural recorder checks, actual JVM tests, Android Release Gradle build, stable public test signing-certificate verification and GitHub Release publication. The game branch `feature/android-native-port` remains read-only at reviewed SHA `6b60c35e845a3bc8e559a7df7e408363032697cb`. Rendering must be fixed in the game, not by the logger; on-device acceptance of any new LogRaft APK remains independent of CI success.

## Verified deliveries

1. [Commit `0025858d`](https://github.com/alwansan/raf/commit/0025858dcede41a50028eed9583828da9b7ecf14) added fixed Logcat-only milestones for FMOD bootstrap, Android startup, scene callback, player callback and `World has been loaded`. [Actions **41895148905**](https://github.com/alwansan/raf/actions/runs/41895148905) **COMPLETED SUCCESS** and [signed LogRaft 0.6.87](https://github.com/alwansan/raf/releases/tag/lograf-87) was released.
2. [Commit `90ac2dca`](https://github.com/alwansan/raf/commit/90ac2dca6b44defd8085941b028b83a07a2737fd) added water-material breakdown, kernel-index grouping, dedicated render-error flood rate and UI/session summaries. [Actions **41896005067**](https://github.com/alwansan/raf/actions/runs/41896005067) **COMPLETED SUCCESS**: structural guard checks, actual JVM regression for FFT/OBB/FM​​OD/PSS/PID/FIFO marker/milestones/render material buckets, Gradle `BUILD SUCCESSFUL in 57s`, signature verification and Release publication.
3. Latest signed APK: [`lograf-88/LogRaft-signed.apk`](https://github.com/alwansan/raf/releases/download/lograf-88/LogRaft-signed.apk), 164,672 bytes; SHA-256 sidecar exists. Version `0.6.88`, automatic `versionCode=1088`, `applicationId=com.alwansan.lograf`. Existing public test certificate SHA-256: `bdb27cfad1fd9a6ac14bd47317206ce4df462040f45ddb1fdbb66a0974043149` (certificate fingerprint, not APK-file hash).
4. **Owner's file was from 0.6.86, NOT 0.6.88.** The new milestone and water-material summary implementation is verified in CI but its accuracy under actual Android 15 Shizuku capture still requires a new phone session. Do not describe the newest build as installed-device-verified.

## External FPS cross-check

A read-only offline comparison used the user's private Unity `raft-logs` alongside timestamp-proximate LogRaft 0.6.86 SurfaceFlinger samples. Of 96 pairs within 2.5 seconds, mean presented FPS was approximately **41.10**, mean Unity-reported FPS approximately **40.72**, median absolute difference **1.76 FPS**. These are **different sampling windows**, with some startup outliers; this only supports plausibility of the SurfaceFlinger *estimate* in that recording, not universal equivalence or guaranteed per-frame correctness. No private telemetry ZIP was committed.

No game branch, other repository, automation schedule, saved game, signing key or original resource was modified.
