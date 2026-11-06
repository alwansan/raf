# T5 PERF-007 — same-UTC Unity timing during stale SurfaceFlinger (6 Nov 2026)

## Engineering question

The owner tested the original signed APK/OBB native run42058825739 on Poco F5 Pro and confirmed world entry/save/reopen, while major water shader/FFT errors remain. Source-pinned LogRaft session `230108-327` shows only 2 fresh SurfaceFlinger FPS measurements (120.77–120.78 during initial startup) and 105 stale telemetry measurements. Does that mean the Unity game stopped producing frames? **No conclusion is possible from SurfaceFlinger alone.**

Four exact source bytes are available at `alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57`:

- External LogRaft `220911-559`: `metrics-...220911-559-00001.jsonl`, Git blob `bb24dda68503897cf4e2a5e4e2d8aef3e71777b8`, 374,587 bytes.
- External LogRaft `230108-327`: `metrics-...230108-327-00001.jsonl`, blob `0327e5a3bb01ca944b2c40e07d49f503914dd274`, 646,527 bytes.
- **Unity persistent app log** from the first phone session: `raft-logs/raft-20261105T190845373-8cee733d-0000.jsonl`, Git blob `413932e92fc24cd50b1fae1cbb25120f392e8158`, 499,456 bytes.
- **Unity persistent app log** from the second: `raft-logs/raft-20261105T200139667-637f8d6a-0000.jsonl`, blob `60674be571e4979e329924e5e2679f43e40ec41a`, 1,443,270 bytes.

The original Unity logs report `area=performance; operation=sample` with explicit `interval_frames`, FPS from Unity unscaled delta time, per-interval frame timing percentiles, scene name, output size/orientation, and sometimes latest `FrameTimingManager` CPU/GPU numbers. Unlike the external SF source, **this game-side telemetry continued even when SurfaceFlinger instrumentation became stale**.

## Preliminary direct cross-check, before CI gate

| Session | Unity performance intervals | Qualifying Unity intervals (≥30 frames, no overflow, landscape) | Scene breakdown of qualifying entire session |
|---|---:|---:|---|
| 220911-559 | 39 | 36 | MainMenuScene 21; MainScene 15 |
| 230108-327 | 123 | 116 | MainMenuScene 36; MainScene 80 |

Within the **second** external session's continuous stale presentation period **2026-11-05T20:02:04.996Z–20:07:48.413Z**, the game-side Unity persistent log records **62 qualifying intervals**, 35 in `MainScene` and 27 in `MainMenuScene`. That is direct evidence of **telemetry-source divergence during the same UTC period**, not proof that these frames reached the screen or that Vulkan shaders were visually correct. It also does not imply a frozen or healthy game.

Scene-specific source readings from all qualifying Unity intervals, not matched world states: MainScene Unity interval FPS median **21.2** in session 220911 and **18.85** in 230108. The reported per-interval frame-p95 median values are **66.17 ms** and **74.57 ms** respectively. These are *medians of individual 5-second interval p95s*, **not** pooled frame p95, and differ in scene activity/world/settings/temperature. Treat as exploratory evidence, not an A/B benchmark or measured performance regression.

## Reproducible code / negative controls

`scripts/t5_cl_unity_surface_bridge.py` validates bounded Unity JSONL sequence monotonicity, UTC stamps, frame-sample sample counts, frame window size, no overflow, positive finite interval FPS and orientation, then time-joins only genuinely stale LogRaft runs to qualifying Unity intervals. It separates scenes and labels the median-of-interval-p95 statistic honestly; it never treats external SF as Unity GPU FPS, or game-side updates as proof of display presentation.

`tests/test_t5_cl_unity_surface_bridge.py` includes synthetic adversarial time-join, stale-gap, scene, missing source, invalid clock/JSON, frame overflow, nonfinite/misordered input and no-clobber controls.

Source-pinned, CPU-only `.github/workflows/raft-t5-cl-unity-surface-bridge.yml` verifies 4 CL Git blob SHA1s from the exact fixed source commit, reads under 3 MB total of public samples (not proprietary game assets or private saves), never uploads raw logs, asserts actual observed counts, and reports aggregates only. **No Unity build**, APK/OBB/release mutation or gameplay code change.

- CI: https://github.com/alwansan/raf/actions/runs/42146299959 (result must be explicitly checked)
- Previous external-only CI: https://github.com/alwansan/raf/actions/runs/42145219506 (18/18 tests, verified NOT_COMPARABLE)
- Session handoff: `prompt/coordination/clients/T5/sessions/20261106T0145Z-T5-chat-unity-surface-bridge-f4c2.md`

## Acceptance boundary

A later performance comparison still requires matched **APK/OBB SHA, same world/viewpoint, same in-game graphics settings/render scale, same scene phase and reproducible frame windows**. GPU busy from KGSL is system-wide. `FrameTimingManager` latest GPU frame numbers can be unavailable/unreliable; do not interpolate or infer work distribution. An exact joined time span indicates game simulation timing output existed while the independent SF probe lacked fresh presentation timestamps; it does not prove human-visible frames or a root cause of performance.

Open P0 water/FFT and graphics issues remain with T1–T3; T4 mouse and T5 scheduled Resolution work untouched. Do not disable shader errors to improve metrics. This evidence task does **not** itself improve FPS or justify READY (0/3).
