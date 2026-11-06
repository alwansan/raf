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

## Verified integration, exact live CI

The first [run42146299959](https://github.com/alwansan/raf/actions/runs/42146299959) **FAILED** only when directly invoking a script that used `from scripts...`; checkout, all 15 source-free tests, and 4 Git blob auth preflight passed. Diagnosed `ModuleNotFoundError: No module named 'scripts'`, not a failure in original telemetry. The surgical fix changes only the workflow invocation to `python3 -m scripts.t5_cl_unity_surface_bridge` in commit `eed7322565944a1d7fccda62fc5f7662f88b5e7e`, retaining all assertions and source pins.

**Final verified result:** [CI42146496632](https://github.com/alwansan/raf/actions/runs/42146496632), job `127659125692`, **COMPLETED SUCCESS** on source `eed7322565944a1d7fccda62fc5f7662f88b5e7e`:

- All **15/15** synthetic time alignment, scene, missing/unsafe input and stale telemetry controls passed. `py_compile` passed.
- All **four actual immutable CL Git blob SHA1s verified**; bytes read 499,456 (Unity A), 1,443,270 (Unity B), 374,587 (SF A), 646,527 (SF B). Only bounded aggregate numeric report printed, no raw private game data archived.
- 220911 Unity performance records **39**, qualified **36**, scene split MainScene 15 / MainMenuScene 21; SF stale samples **6**, no qualified Unity intervals inside the bounded stale window.
- 230108 Unity performance records **123**, qualified **116**, scene split MainScene **80** / MainMenuScene **36**; SF stale samples **105**, while **62** qualified Unity intervals were written in the same bounded stale span. Of those 62, **35 MainScene** and **27 MainMenuScene**.
- During 230108 stale SF window, scene-specific Unity interval FPS medians: **17.99 MainScene** and **22.77 MainMenuScene**. The medians of *per-interval* frame-p95 metrics are **82.83 ms MainScene** and **66.25 ms MainMenuScene**. These are **not pooled per-frame percentiles**. Their evidence shows nontrivial game frame processing during the independent SF metric gap, not reliable on-screen present timestamps.
- Full 230108 MainScene qualified Unity interval median FPS **18.89**, and median-of-interval-p95 **74.57 ms**; first session MainScene **21.20 FPS**, median-of-interval-p95 **66.17 ms**. The sessions are different world/thermal/motion/settings contexts. **No cross-session performance improvement/regression claim is justified**.

**Consequence:** The repeated 120Hz SurfaceFlinger startup readings in 230108 should not be used as gameplay FPS; external SF telemetry stale for 105 samples does not prove Unity stopped executing or that the game was visually healthy. Prefer the separately instrumented Unity `performance.sample` for diagnosis with its own provenance/scene/interval caveats. No runtime/profile code changed and no new APK device acceptance claimed. PERF-007 remains open, overall NOT_READY 0/3.
