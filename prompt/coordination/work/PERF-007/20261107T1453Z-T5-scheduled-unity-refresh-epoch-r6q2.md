# 20261107T1453Z-T5-scheduled-unity-refresh-epoch-r6q2
origin: scheduled
role: T5
issue_id: PERF-007 / DISPLAY-003
baseline_sha: ffa2309de8d3e2d15630d394b2f5b1ee6a3e828b
status: completed
intended_files: prompt/coordination/work/PERF-007/20261107T1453Z-T5-scheduled-unity-refresh-epoch-r6q2.md; prompt/coordination/clients/T5/sessions/20261107T1453Z-T5-scheduled-unity-refresh-epoch-r6q2.md
experiment_key: CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57:raft-logs/9:unity-performance-sample:scene-refresh-epoch:v1
resource_key: none; read-only CL telemetry, no Unity
hypothesis: Unity-internal FPS samples change refresh_hz across a single session, so pooling across menu/game or display-refresh epochs is unsafe. This is distinct from T5's prior SurfaceFlinger cohort test.
taken_over_from: docs/T5_REAL_CL_PERFORMANCE_COHORT_2026-11-06.md and T5 session 20261107T1349Z-T5-scheduled-right-geometry-k9p4.
coordination: T4 owns mouse, T1/T2 water, T3 materials; no shared source modifications or native CI.
result: Inspected 1542 genuine Unity JSONL records across two source-pinned CL game logs (115 performance samples); identified a reported 120Hz to 60Hz change in the second process session while 2400x1080 Landscape remained unchanged. Split by scene/refresh; rejected startup frame_samples<30 for sample median. Full results and limits in session 20261107T1453Z-T5-scheduled-unity-refresh-epoch-r6q2.md. Third larger log unavailable via connector; no controlled device comparison. No Unity/CI requested.
next: Build fail-closed Unity-internal performance epoch gate; inspect third file in bounded pinned CI; match APK+OBB before cross-build comparison.
