# 20261107T1453Z-T5-scheduled-unity-refresh-epoch-r6q2

origin: scheduled
role: T5
baseline_sha: ffa2309de8d3e2d15630d394b2f5b1ee6a3e828b
plan_commit: b87544fc47feb501b4cd0b97bdbc0eadd2c880d6
resumed_from: 20261107T1349Z-T5-scheduled-right-geometry-k9p4; 20261106T0138Z-T5-chat-performance-cohort-7ab4
issue: PERF-007 / DISPLAY-003

## Distinct new evidence: game-internal Unity performance stream

Read-only original CL source snapshot [520c4cf409aa20a4db54ff80ed87d8807d9cba57](https://github.com/alwansan/CL/tree/520c4cf409aa20a4db54ff80ed87d8807d9cba57/raft%20log) at `انتاج مسار /9/com.alwansan.raft.androidtest/files/raft-logs`. Inspected **full JSONL** for `raft-20261105T190122615-4e37ab3f-0000.jsonl` (898 records, 76 `area=performance, operation=sample`) and `raft-20261105T190845373-8cee733d-0000.jsonl` (644 records, 39 samples). A third 1,443,270-byte file `raft-20261105T200139667-637f8d6a-0000.jsonl` exceeded connector's raw-file read limit and is **not inspected**. No claims about third file.

Parsed semicolon-delimited `detail` fields on each performance sample, retaining original scene, refresh_hz, interval_frames, frame_samples, fps, frame_p50_ms, frame_p95_ms, width, height and UTC. Excluded startup samples with frame_samples < 30 for reported sample-FPS medians. **Medians below are medians of interval FPS samples, not pooled per-frame p50/p95**; per-interval p95 median is separately labeled. No samples merged across scenes or refresh rates.

| Game log | Scene and refresh epoch | Total samples | Qualified >=30 frames | Median of interval FPS | Median of interval frame-p95 (ms) |
|---|---|---:|---:|---:|---:|
| 190122615 | MainMenuScene 120Hz | 28 | 27 | 36.04 | 33.17 |
| 190122615 | MainScene 120Hz | 48 | 48 | 29.50 | 41.36 |
| 190845373 | MainMenuScene 120Hz | 21 | 19 | 24.21 | 57.91 |
| 190845373 | MainScene 120Hz | 16 | 15 | 21.20 | 66.17 |
| 190845373 | MainMenuScene 60Hz | 2 | 2 | 18.64 | 99.37 |

**New decisive observation:** the second original game log changes from **120Hz to 60Hz** between `2026-11-05T19:12:55.9473390Z` (MainMenuScene, refresh_hz=120) and `2026-11-05T19:13:00.7316840Z` (MainMenuScene, refresh_hz=60). Both records still say width=2400, height=1080, Landscape. This is a **reported refresh-hz transition**, not proof of which Android subsystem requested it, a Resolution dropdown change, or a change to internal render scale. The last two 60Hz samples are insufficient for a stable performance comparison. No 60Hz transition was observed in first game's 76 sampled intervals.

Both files include MainScene and MainMenuScene intervals; scene transitions are visible in separate `area=scene` records. Do not pool a session-wide FPS median, compare menu vs world as an optimization, equate 120Hz display to 120FPS, or equate `gpu_latest_frame_ms` with independent GPU busy/complete GPU workload. Scene, refresh, startup and capture-window gates must be explicit. The two files are distinct process sessions, but not controlled same-scene/same-temperature matched runs. The first file includes MainScene after 19:04:06Z, the second after 19:10:39Z. The second log returns to MainMenuScene before the late 60Hz samples.

Prior independent SurfaceFlinger report `docs/T5_REAL_CL_PERFORMANCE_COHORT_2026-11-06.md` remains valid within its own telemetry semantics: its 57/2 fresh presented-frame samples are **not** these Unity game-internal samples, and no cross-source p95 is calculated.

## Acceptance boundary and next step

This is original read-only telemetry analysis, not new phone testing, FPS improvement, causal evidence of Resolution behavior, APK/OBB binary match or completed Unity render-scale implementation. The owner-reported world/save/re-entry success belongs only to native run [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) source e9c358ed. T4 owns physical mouse; three right buttons already have source regression tests; do not duplicate or change working Settings blindly.

Next implement a **fail-closed Unity-internal frame epoch parser** for these original JSONL records: reject mixed scene/refresh cohorts, unknown/invalid interval sample counts and startup outliers; report interval medians without calling them pooled per-frame quantiles. Cross-check Android display mode/window/render scale instrumentation and tie each run to signed APK+OBB hashes. The 1.44MB third file requires a bounded GitHub Actions read (pinned CL Git blob) rather than an unverified partial download. Compare later build only on same phone/world/settings/refresh with verified package identity. No native build requested; readiness NOT_READY 0/3.
