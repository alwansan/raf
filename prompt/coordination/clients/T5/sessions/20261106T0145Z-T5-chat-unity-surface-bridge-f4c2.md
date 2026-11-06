# T5 chat — 20261106T0145Z-T5-chat-unity-surface-bridge-f4c2
- origin=chat
- session_id: 20261106T0145Z-T5-chat-unity-surface-bridge-f4c2
- base_sha: 726035aa11c5a7f2b43e7cc51db8a255498fed5c
- status: active
- resumed_from: 20261106T0138Z-T5-chat-performance-cohort-7ab4; scheduled 20261106T0047Z-T5-scheduled-c4e8; chat OBB verified 20261105T2208Z.
- work: prompt/coordination/work/PERF-007/20261106T0145Z-T5-chat-unity-surface-bridge-f4c2.json
- experiment_key: t5-realCL-520c4c-20261105-surface-stale-window-game-side-frame-same-utc-join-v1
- selected resource: CL-4-pinned-readonly-metrics-and-unity-logs-total-under3MB
- direct pre-CI observation: first actual Unity game log 413932e9.. has 39 performance intervals, second game log 60674be5.. has 123; 36 and 116 qualify at >=30 frames. External second SF stale from 2026-11-05T20:02:04.996Z through 20:07:48.413Z, 105 stale samples. Within this window, actual Unity log recorded 62 qualifying performance intervals (35 MainScene, 27 MainMenuScene).
- strictly separate Unity Update interval FPS, SurfaceFlinger presentation and system-wide KGSL busy; scene+resolution alone not same-world proof. Do NOT infer that Unity timing proves actual presented frames.
- planned new scripts/tests/workflow/report listed in prompt/coordination/work/PERF-007/20261106T0145Z-T5-chat-unity-surface-bridge-f4c2.json, no game source/Unity build/Release/APK/OBB, no T5 scheduled Resolution, T1-T4 code changes.
- next: test strict source SHA/time alignment and fail-closed scene/window summaries on pinned real CL files.

## Real-source CI completion (2026-11-06 01:51 UTC)
- [CI42146299959](https://github.com/alwansan/raf/actions/runs/42146299959) failed at Python script-mode `ModuleNotFoundError: scripts`, after 15/15 synthetic tests and all four CL original blob SHA preflight passed. No interpretation of game logs was used to disguise failure.
- Minimal fix: workflow invokes `python3 -m scripts.t5_cl_unity_surface_bridge` in commit eed7322565944a1d7fccda62fc5f7662f88b5e7e, with original tests/source pins unchanged.
- [CI42146496632](https://github.com/alwansan/raf/actions/runs/42146496632) **COMPLETED SUCCESS**, job 127659125692; 15/15 source-free tests (0.005s), py_compile, read and verified all four exact original CL blobs, actual UTC grouped join passed all exact assertions.
- Session 220911: 39 Unity performance intervals, 36 qualified (MainScene15/MainMenuScene21), SF stale6; qualified Unity within SF stale 0.
- Session 230108: 123 Unity performance intervals, 116 qualified (MainScene80/MainMenuScene36), SF stale105; **62** qualified Unity performance samples during actual same UTC SF stale window, **35 MainScene** and **27 MainMenuScene**. Game-side time-window median fps **17.99 MainScene**, **22.77 MainMenuScene**, median-of-interval-p95 **82.83ms/66.25ms**, respectively. These do not prove presented frames, pooled frame p95, or same-viewpoint comparable sessions.
- New source script scripts/t5_cl_unity_surface_bridge.py, tests/test_t5_cl_unity_surface_bridge.py, workflow .github/workflows/raft-t5-cl-unity-surface-bridge.yml and docs/T5_CL_UNITY_SURFACE_BRIDGE_2026-11-06.md; experiment/event stored under matching session ID.
- No changes to actual Unity runtime, T5 scheduled Resolution, T4 mouse, T1/T2/T3 shaders, Audio, Steam, resource GUID, native artifact, LFS, Release, or private telemetry sharing. PERF-007 open, full game readiness NOT_READY 0/3.
- next_step: same-scene, same-ABI+APK/OBB SHA and quality/render-scale tagged Unity frames and device present audit on a future legitimately tested build. Do not claim 120FPS startup performance or a device hang from SF telemetry.
- status: completed_real_source_verified

## Team source-evidence index follow-up
- [CI42146886344](https://github.com/alwansan/raf/actions/runs/42146886344) COMPLETED SUCCESS: canonical T_TEAM refresh script reran against branch; first push raced with another client and failed safely (no force). Bounded re-fetch found generated index already current, exited `T5_LEDGER_REFRESH already_current=true`. The verified T5 experiment/event files remain recorded independently.
- Preserve final verified performance evidence on immutable original CL four blobs and source CI42146496632. Do not equate any CI result to a new playable APK; WATER-001/RENDER-002 and PERF-007 remain OPEN.
