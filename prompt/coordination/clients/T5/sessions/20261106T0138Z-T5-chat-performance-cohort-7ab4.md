# T5 chat: 20261106T0138Z-T5-chat-performance-cohort-7ab4
- origin: chat
- session_id: 20261106T0138Z-T5-chat-performance-cohort-7ab4
- baseline_sha: 6421459579fa5e0c006a088cb30ecf76f023e129
- status: active
- resumed_from: T5 chat 20261105T2208Z patch OBB exact classification; T5 scheduled 20261106T0047Z resolution audit (separate ownership); owner device report
- work: prompt/coordination/work/PERF-007/20261106T0138Z-T5-chat-performance-cohort-7ab4.json
- scope: PERF-007, read-only LogRaft SurfaceFlinger freshness/error-onset cohort; scripts/tests/one source-only workflow/new report only
- source CL pinned tree 520c4cf409aa20a4db54ff80ed87d8807d9cba57; JSONL blob bb24dda68503897cf4e2a5e4e2d8aef3e71777b8 (220911-559, 71 rows), 0327e5a3bb01ca944b2c40e07d49f503914dd274 (230108-327, 119 rows).
- preliminary source observation: first session 57 valid SurfaceFlinger FPS and 6 stale telemetry; 2nd session only 2 valid samples at 120.77/120.78 before render errors start at sample16, then 105 stale. No comparative performance conclusion.
- caution: SurfaceFlinger presentation estimates not Unity FrameTiming, KGSL GPU busy system-wide; no causal thermal/gpu interpretation or multi-session mean averaging.
- experiment_key: t5-CL520c4c-20261105-version89-two-sessions-performance-fresh-surface-same-rendererror-cohort-v1
- files/experiment and resource registered before implementation; no T5 scheduled Resolution, T1/T2 water, T3 materials, T4 input, Unity, OBB files or release touched.
- next: strict time/pid/freshness/evidence tests and source-authenticated real pinned CI; document non-comparable verdict, avoid disclosing raw user logs.

## Verified closeout — 2026-11-06 01:39 UTC
- [CI42145219506](https://github.com/alwansan/raf/actions/runs/42145219506) COMPLETED SUCCESS; exact source 7c0f7fb78a178d32c3539b35b661a848ffa8a9b9; job127654944860. 18/18 synthetic tests passed (0.005s).
- Two actual public CL JSONL blob SHAs validated via Git SHA1, byte sizes 374587 and 646527. 190 real sample rows inspected; source-only file input, no raw private logs/assets uploaded.
- Actual result: 220911-559 57 fresh FPS all post-render-error, stale6, median presented 23.87 (not Unity); 230108-327 only 2 startup 120.77/120.78 pre-error, stale105, zero valid post-error. NOT_COMPARABLE.
- New non-overlapping observation after CI: game-side Unity persistent log blobs 413932e92fc24cd50b1fae1cbb25120f392e8158 and 60674be571e4979e329924e5e2679f43e40ec41a contain 39 and 123 performance interval entries respectively, separate from SurfaceFlinger. Need qualified scene/window analysis in new work scope; absence external SF timestamps does not imply game stopped.
- Scope files scripts/t5_cl_fps_cohort_gate.py, tests/test_t5_cl_fps_cohort_gate.py, .github/workflows/raft-t5-cl-real-fps-cohort.yml, docs/T5_REAL_CL_PERFORMANCE_COHORT_2026-11-06.md. Evidence prompt/coordination/experiments/T5/20261106T0138Z-T5-chat-performance-cohort-7ab4.json; event prompt/coordination/B_TEAM/events/T5/20261106T0138Z-T5-chat-performance-cohort-7ab4.json.
- Did not modify Unity, source code of game, T5 Resolution, T1–T3 graphics, T4 mouse, water asset/provider, OBB/Release, nor cancel Action. Overall readiness NOT_READY 0/3; current scope completed.
- status: completed_source_and_actual_CL_verified
