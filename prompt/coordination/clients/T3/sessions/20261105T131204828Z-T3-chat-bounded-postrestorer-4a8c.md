# T3 — original bounded export before/after verified ShaderLab vendor restorers

- identity: T3; origin: chat; session_id: `20261105T131204828Z-T3-chat-bounded-postrestorer-4a8c`; status: waiting_ci
- resumed_from_sessions: `20261105T124551Z-T3-chat-subshader-coverage-c29b`, `20261105T1213Z-T3-native-shader-dummy-audit`
- base_sha: `76b0b1dceab3d6cfdad4f99570a448c9975b3704`; branch: `feature/android-native-port` only
- work: `prompt/coordination/work/RENDER-002/T3-20261105T131204828Z-T3-chat-bounded-postrestorer-4a8c.json`; experiment_key: `T3-ZIP2-15964ea8f246b6e076ce26b60931ee2e1a9a2385-12-owners-AssetRipperCLI-036098ab5-B21Export-9.0-TMP3.0.6-PostFX933df236-Volumetricd20b6f9-nat-restorer-quality-audit`
- same evidence: [CI42026630845](https://github.com/alwansan/raf/actions/runs/42026630845) confirms 511/511 custom Materials reference Dummy ShaderLab before vendor restorers in genuine 12-owner export; [CI42030761276](https://github.com/alwansan/raf/actions/runs/42030761276) passed T3 diagnostic synthetic checks. Neither proves post-restorer Unity/Adreno.
- 2026-11-05 review: no queued/in_progress workflow runs; T1 FFT, T2 Foam, T4 world, T5 integration separate. No current native full import run; do not dispatch it or cancel other work.
- hypothesis: a bounded actual original same-instance vendor restoration should determine whether TMP/PostFX/Volumetric source replacements remove any custom Material-linked dummy programs, without falsely claiming full native output or Android pixels.
- planned files: `.github/workflows/raft-t3-bounded-postrestorer-shader.yml`, this session, per-session work/experiment/event only. No game shaders, .meta, prefab/scenes, audio/Settings/touch, Unity production workflow or APK changes.
- pinned source: ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, 12-owner SHA manifest and previous verified export pipeline; actual pinned official vendors in restoration scripts. No raw original assets or source in public report/artifacts.
- budget: isolated 2-core real export, 35-min ceiling, no runner cancellation; safe aggregate before/after and immutable original existing .shader.meta comparison. All original importer assets remain untouched.
- result: Workflow committed `dcb81c72b91817872cacc0fd664d937ea2f9ddef`; [CI42033940194](https://github.com/alwansan/raf/actions/runs/42033940194) in progress (source-free tests already passed, real exporter compilation underway at first checkpoint). If any official vendor has no original Shader identity in bounded sample, do not infer full native restoration.
- next_step: inspect CI42033940194 status, uploaded SAFE pre/post counts (if any), distinguish bounded restorer presence/absence, preserve metadata and RENDER-002 OPEN. No repeated heavy run while active.
