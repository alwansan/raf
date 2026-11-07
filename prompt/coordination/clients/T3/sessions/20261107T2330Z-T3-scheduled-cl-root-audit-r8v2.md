# T3 scheduled session — 20261107T2330Z-T3-scheduled-cl-root-audit-r8v2
origin: scheduled
issue: RENDER-002 OPEN / NOT_READY
base_sha: 618fdff09190d22cf41245c93b24fa00ac029336
resumed_from_sessions: 20261107T2230Z-T3-scheduled-render-device-chain-k4p9 and 20261107T0927Z-T3-scheduled-artifact-provenance-k7m2
work: prompt/coordination/work/RENDER-002/20261107T2330Z-T3-scheduled-cl-root-audit-r8v2.md (scope commit b6326bee9ec76ba02262fef09715c0c12dd19fb4)

## Actual new verification
Read owner phone report, AGENTS, CURRENT_OWNER_REQUIREMENTS, STATUS, T_TEAM operating and chat/scheduled instructions; checked HEAD and recent Actions (20 most recent completed, no queued/in_progress in that window). Read CL at immutable snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 **directly**: two session-summary.json files, not just the owner report. Their raw log segments exist (2 x ~33MB for 220911; 4 segments for 230108), but individual raw messages and screenshot pixels were NOT inspected this session.

Session 220911-559 final 23,884 UltimateWater invalid-pass roots = 8,484 spectrum + 15,400 foam_global (64.48% foam); 3,850 kernel-index-6 roots; 1 OBB GUID failure; 1,333 cursor RGBA32 warnings; 1 missing Mono script; 1 duplicate EventSystem; 4 convex polygon warnings. Recorded world_loaded milestone once. 57 valid SurfaceFlinger estimates, mean 22.29 FPS; not Unity/GPU FPS. Writer failed batches 0, but Android Logcat ring losses unmeasured.

Session 230108-327 final 39,132 UltimateWater invalid-pass roots = 15,028 spectrum + 24,104 foam_global (61.60% foam); 6,026 kernel-index-6 roots; 2 OBB GUID failures; 2,977 cursor RGBA32 warnings; 1 missing Mono script; 1 duplicate EventSystem; 4 convex polygon warnings. World_loaded once. Only 2 readable SurfaceFlinger estimates; **do not report 120.78 as gameplay FPS** (105 stale samples). Writer failed batches 0, but Android ring losses unmeasured.

Both source summaries report missing_asset_errors_total_at_last_sample=0, which means the instrumented category saw no such errors, NOT that textures, Material PPtrs, shader variants or asset payloads are complete. No source summary explicitly attributes white hand/raft or square smoke to UltimateWater. Water-pass breakdown belongs to T1/T2; square smoke requires ParticleSystemRenderer->Material->Shader->blend/alpha->texture investigation, while white objects need mesh/material/shader variant and texture importer checks.

Source of truth: https://github.com/alwansan/CL/tree/520c4cf409aa20a4db54ff80ed87d8807d9cba57/raft%20log/lf ; phone run https://github.com/alwansan/raf/actions/runs/42058825739 (source e9c358eda01785b65e4eb14f18723da426635628). Previous authentic 41 Material/227 TexEnv/150 RGBA parity remains narrow and does not prove device visuals.

## Result / limits / next
Result: independently corroborated per-material water error root breakdown and validated that the 230108 FPS reading is insufficient, without falsely assigning white/smoke root cause. No source code, assets, .meta, GUID, .rgd, audio, Settings, touch, native build, CI or release modified. T3 vote 'لا يحتاج' until substantive visual integration evidence.
Next: read bounded individual CL messages around world_loaded and capture screenshot pixels; identify smoke ParticleSystemRenderer and white hand/raft renderer Material/Shader GUIDs from pinned original/export graph; design one discriminating ShaderLab/alpha/texture experiment. Do not repeat classifier-only changes without private original per-pair metadata.
