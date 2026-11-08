# T5 scheduled — original LogRaft metrics schema audit

- session_id: 20261108T0050Z-T5-scheduled-lograft-schema-audit-v6p2
- origin: scheduled
- UTC: 2026-11-08T00:50Z
- base_sha: 9412a624464034600981f026046c95aceea218fb
- resumed_from_session: 20261107T2252Z-T5-scheduled-scene-transition-k7m4; earlier T5 performance CI 42408172119.
- owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, owner-confirmed world/save/reopen on old source e9c358eda01785b65e4eb14f18723da426635628 only.
- scope: read-only CL original LogRaft metrics and analyzer regression; no T4 mouse files, Unity, shaders, APK, OBB or releases.

## Verified evidence

1. GitHub Actions [42426715134](https://github.com/alwansan/raf/actions/runs/42426715134) completed SUCCESS on 370693bf7b9d1b68c53d1f168d3c58b710a573dc, after scene-boundary test commit. This is source-only CI, not original device replay.
2. Read original immutable CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57 at `raft log/lf/LogRaft-20261105-220911-559/metrics-20261105-220911-559-00001.jsonl` lines 1–12. Records have `schema:1`, `source:lograf_shell`, `timestamp_unix_ms`, `presented_fps_estimate`, `fps_quality`, `fps_method: SurfaceFlinger --latency game SurfaceView (NOT Unity Update FPS)`, `gpu_busy_percent`, `unity_frame_gpu_ms:null`, `unity_frame_timing_reason: Requires game-side Unity FrameTimingManager diagnostics`. Samples 1–4 have unavailable presented FPS. These records **are not** `area=performance;operation=sample;detail=...` Unity internal rows expected by `scripts/t5_unity_interval_epoch.py`.
3. The Unity analyzer silently ignores those shell metrics because `area` is absent; passing them to it would return zero intervals, not evidence of zero frames. `gpu_busy_percent` is KGSL system-wide busy/total, not per-frame GPU milliseconds or necessarily game-only load. Do not pool the shell SurfaceFlinger estimate with Unity FPS.
4. `scripts/test_t5_scene_epoch_boundary.py` has 3 synthetic scene-transition cases. Source-only CI passed; original CL scene-event names and actual APK/OBB cryptographic identity remain unverified.
5. Trial-build round trial-20261106-r1 remains non-unanimous in latest inspected ledger (T4 needs, T1/T2/T3/T5 no); no new native request.

## Decision / limits

Schema mismatch is established by the original CL source and current analyzer. No claim of improved device FPS, APK/OBB identity, GPU frame time, or actual scene boundary recognition. No runtime code was changed. Separate a dedicated LogRaft shell metrics cohort parser with explicit quality flags from Unity internal interval parser; only join by verified session/package/time provenance. This is a reproducible provenance decision, not a phone test.

## Next

Inspect `session-summary.json` and original internal game logs for `area=scene`/operation schema, then add fail-closed provenance adapter/tests for shell metrics with SurfaceFlinger-quality filtering; match signed APK/OBB manifest and hashes before any cross-version comparison. Preserve T4 mouse and T5 UI/Resolution scopes; do not dispatch duplicate Unity.
