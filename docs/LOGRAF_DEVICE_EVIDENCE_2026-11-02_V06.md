# LogRaft 0.6.51 device stress evaluation — 2 Nov 2026

## Source and limits

Two user-provided ZIP recordings, `LogRaft-1793642162566.zip` (session `20261102-205325-994`) and `LogRaft-1793642351692.zip` (session `20261102-205608-054`), captured on Xiaomi 23013PC75G, Android 15, LogRaft v0.6.51. Only aggregate numbers and crash/process facts below are retained in this repository; raw recordings remain with the user.

**These are recorder and external system observations, not controlled game performance comparisons.**

## Verified recorder performance

| Measurement | Session 20:53:26–20:56:01 | Session 20:56:13–20:59:10 |
|---|---:|---:|
| Logcat UID lines | 1,384,312 | 2,021,696 |
| Local queued batches received/written | 4,284 / 4,284 | 6,152 / 6,152 |
| Locally failed batches | 0 | 0 |
| Largest pending queue | 262,485 bytes | 196,900 bytes |
| Worst local queue wait | 158 ms | 93 ms |
| Stream reconnects | 0 | 0 |
| Process CPU peak | 231.66% of one core | 318.98% of one core |
| RSS peak | 1,087,992 KiB | 2,214,412 KiB |
| GPU busy max (device-wide) | 99.76% | 67.63% |
| FPS valid samples | 0/49 | 7/55 |
| Error: invalid shader pass | 49,706 | 71,670 |
| Error: invalid compute kernel | 4,142 | 5,941 |
| Missing haptics asset path errors | 35 | 35 |

The bounded writer now successfully persisted every batch **accepted by its own queue**. That is not proof that Android's upstream rotating Logcat buffer never lost lines.

## Important exit evidence

At 20:55:58 local time in session 1, Android Logcat recorded process death for **PID 20115**. Its matching ApplicationExitInfo row reported `reason=2 (SIGNALED)`, `status=9` (**SIGKILL**) and `subreason=0 UNKNOWN`. The signal sender and motivation cannot be identified from these fields alone. Android system memory did not reach a demonstrated out-of-memory threshold in the sampled telemetry, so do not declare OOM, lmkd, or a Java/native exception the proven cause.

In session 2, the game **PID 22545** died at 20:59:07.408 while the final metrics sample was at 20:59:06.472, and manual Stop followed shortly afterward. The 3-second telemetry loop missed the process-exit history. New branch changes add a final package- and PID-matched `dumpsys activity exit-info` lookup on Stop to capture that evidence even when no later 3-second sample is available.

## FPS defect observed and fixed in source

Session 1: 39 `insufficient_presentation_samples` and 7 `surface_latency_unavailable` results while game running; **zero readable FPS**. Session 2: 7 valid FPS estimates during the first ~30 seconds, then 45 unavailable readings while game running. `frame_telemetry_stale` incorrectly stayed false in both sessions because it depended on `lastFrameProgressMs`, which remained uninitialized or could reset when SurfaceView changed.

The new tracking measures elapsed time since the current game PID was first observed or since the latest valid FPS, regardless of whether SurfaceFlinger later returned an invalid/empty buffer or a new layer. It distinguishes `fps_never_available` from `fps_lost_after_valid_samples`; neither proves the game itself froze.

## Next device validation

1. Install the next release signed with the same `lograf-public` certificate, as an update (do not clear app data).
2. Launch LogRaft/Start, then Raft; sample through first visible gameplay and water-heavy scenes, mark a visible issue, and Stop.
3. In `metrics-*.jsonl`, examine `fps_unavailable_duration_ms`, `fps_valid_sample_count`, `frame_telemetry_gap_kind`, `frame_telemetry_stale`.
4. In `session-summary.json`, examine `stop_time_android_process_exit_info`, verifying `matched_pid` against `am_proc_died`, plus writer loss counters.
5. For a SIGKILL event, collect corroborating Android system logs (e.g. explicit ActivityManager `am_kill` or `lmkd`) before attributing responsibility. Do not equate every `reason=SIGNALED status=9` with OOM.
6. In `performance_statistics.error_category_breakdown`, compare shader and compute error frequency to the same game build/scenario.
