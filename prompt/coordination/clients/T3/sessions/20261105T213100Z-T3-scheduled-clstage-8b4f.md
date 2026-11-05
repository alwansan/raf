# T3 scheduled — genuine CL render-error onset relative to world-loaded milestone

- session_id: `20261105T213100Z-T3-scheduled-clstage-8b4f`; origin: scheduled; identity: T3; status: completed (bounded CL diagnostic only).
- base_sha: `df6c913c249c09d4aa7cf58dee6723160e99ddba`; work: `prompt/coordination/work/RENDER-002/20261105T213100Z-T3-scheduled-clstage-8b4f.json`.
- resumed_from_sessions: `20261105T2034Z-T3-scheduled-7c91`, `20261105T211313Z-T3-chat-particle-shader-rank-4e92`.
- Input: read-only CL immutable tree `520c4cf409aa20a4db54ff80ed87d8807d9cba57`, actual session-info.txt and session-summary.json from `lf/LogRaft-20261105-220911-559` and `lf/LogRaft-20261105-230108-327`. These are **LogRaft** logger versionCodes 1088 and 1089, **not** Raft APK versionCode; the game artifact source is `e9c358eda01785b65e4eb14f18723da426635628` only per owner report, actual installed package manifest remains to be matched.
- Owner report: `docs/DEVICE_FEEDBACK_42058825739_AR.md`; owner personally confirmed world/save/exit/reopen on run 42058825739; this does not validate graphics.
- Existing independent T3 original source result: [CI42110973101](https://github.com/alwansan/raf/actions/runs/42110973101) 215 Particle Shader48 slots in six originals; 108 slots on top-ranked shader; subsequent [CI42112666211](https://github.com/alwansan/raf/actions/runs/42112666211) success for source state. Neither proves screenshot emitter association.
 
## Genuine two-session temporal differential (new observation)

Compute `world_loaded_message_observed.first_observed_unix_ms - ultimate_water_invalid_pass.first_observed_unix_ms` and equivalent FFT from **final** session summaries, not mixed telemetry snapshots.

| CL session | first water invalid-pass | first FFT kernel | first world loaded | water precedes world | FFT precedes world |
|---|---:|---:|---:|---:|---:|
| 220911-559 | 1793905782604 | 1793905782606 | 1793905840642 | **58,038 ms** | **58,036 ms** |
| 230108-327 | 1793908926108 | 1793908926110 | 1793909045761 | **119,653 ms** | **119,651 ms** |

Both error classes began **before** the first observed world-loaded message in both independent captures. This rejects the narrow hypothesis that invalid water passes and kernel-6 errors are only activated by the playable-world stage. It does **not** prove the same errors render the menu smoke, or that the first observed message equals first executed world load; log coverage and earlier scene changes are unknown.

Root final breakdown: 220911 water 23,884 = spectrum 8,484 + foam_global 15,400; kernel index6 3,850. 230108 water 39,132 = spectrum 15,028 + foam_global 24,104; kernel index6 6,026. Both source totals reconcile exactly. No missing-asset errors counted in these summaries; that is **not** proof of complete textures, meshes, GUID links or healthy OBB. The actual source report contains screenshots of white hand/raft and square smoke; no original emitter or Material identity is logged by these summary files.

## Conclusions and next

**New discriminant:** renderer-water failure is active already during pre-world initialization/menu-time window; isolate water passes independently from particle Shader48. A single white surface or square smoke screenshot is insufficient to blame water, source texture loss, or top particle shader. For actual square-smoke attribution, inspect the screenshot and the specific menu/particle prefab emitter Renderer→Material→Shader GUID in original ZIP2 and the installed build's exported shader binding. Do not alter the 108-slot particle source code or duplicate T3 chat's render-state workflow. Coordinate with T1/T2 for pre-world spectrum/foam errors and T5 for actual signed package manifest.

**Evidence limits:** only precomputed logger summaries were inspected, not the 33–109MB raw Logcat segments or pixels. Logger versionCodes cannot identify Raft build. No Unity/Android code, assets, .meta, GUID, .rgd, Settings, sound, input, or native workflow modified. No new CI run. RENDER-002 OPEN; NOT_READY (0/3). Next scheduled cycle: choose independent screenshot→emitter binding experiment, checking live T3 chat scope first.
