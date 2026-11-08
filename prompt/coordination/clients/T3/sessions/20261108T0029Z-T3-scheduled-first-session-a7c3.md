# T3 scheduled — independent first CL session render/exit audit
session_id: 20261108T0029Z-T3-scheduled-first-session-a7c3
origin: scheduled
issue_id: RENDER-002
base_sha: 84b3499acf63dc6a86e4722e3affbe0cb8b1d9d0
scope_commit: 639ae716076173ce60bccc33b2cd5757d2b165d0
resumed_from_sessions: 20261107T2330Z-T3-scheduled-cl-root-audit-r8v2; 20261107T2230Z-T3-scheduled-render-device-chain-k4p9
work: prompt/coordination/work/RENDER-002/20261108T0029Z-T3-scheduled-first-session-a7c3.md
status: completed (evidence-only); RENDER-002 OPEN / NOT_READY

## New directly inspected immutable device evidence
Source: alwansan/CL commit 520c4cf409aa20a4db54ff80ed87d8807d9cba57, `raft log/lf/LogRaft-20261105-220101-932/session-summary.json`, schema 1. Earlier T3 2330Z audit read **only** 220911-559 and 230108-327. This fills the omitted first November 5 session, not a rerun of either later summary.

- 76,592 UltimateWater invalid-pass root lines: **46,517 foam_global** (~60.7%), **30,075 spectrum** (~39.3%), zero recorded subsurface_blur/utility_noise. 11,627 invalid kernel-index-6 roots; kernel-index association is not independent proof of UltimateWater origin.
- 6,821 Unity cursor RGBA32 warnings, 2 OBB GUID load failures, one missing Mono script, one duplicate EventSystem, four convex-mesh warnings.
- World-loaded milestone **one** at Unix ms 1793905447216, following three scene callbacks and one player-add callback; this is a log milestone, not direct proof of save/reload in this specific session. Owner's separate phone report confirms save/re-entry for artifact 42058825739.
- Exit-info matched PID 5978, reason SIGNALED, signal 9, subreason UNKNOWN, observed Android death timestamp 2026-11-05 22:08:15.680. **Do not claim OOM or intentional user kill**: sender/motive unknown. LogRaft stop_reason 'Stopped by user' describes logger stop, not proven game termination cause.
- Log writer: 6,878 received/written batches, 0 failed; 7 raw segments, 213,131,955 recorded bytes, 2,120,130 final game log lines. This does not exclude Android Logcat ring losses.
- SurfaceFlinger FPS estimate has **3** readable samples of 133, 119 stale; mean 97.31 is **not** a representative gameplay or GPU FPS. Process CPU across all cores mean 31.43% in 127 samples, GPU busy KGSL system-wide mean 50.28% (130 samples); neither establishes GPU shader cost or device frame rate. PSS can exceed proc RSS for this data; do not equate their means.
- Compared to later T3 verified summaries: 220911-559 23,884 pass/3,850 kernel; 230108-327 39,132 pass/6,026 kernel. First session totals are higher, **but sessions differ in duration and scene**, so raw counts cannot establish regression or improvement. For the first session the invalid-pass observations span ~383.8 s; sample window and error rate require normalization before comparison.

## Attribution / discrimination
These findings establish pervasive water pass/kernel error flooding during a session that reached world_loaded. They **do not** identify the shader responsible for white hand/raft or square smoke. Those need screenshot pixel inspection and source-backed ParticleSystemRenderer->Material->Shader PPtr->Blend/Alpha/texture chain, plus separate material/shader variant trace for white geometry. T1/T2 water repair scope untouched; T4 mouse and T5 resolution/UI untouched. Prior authentic 41 Material/227 TexEnv/150 RGBA parity does not prove Android rendering.

## Limits / next
Read owner feedback, AGENTS, owner requirements, STATUS, T_TEAM operating/chat/prompt, T3 state/MEMORY, previous latest session and branch HEAD. Checked recent Actions list (latest T5 regression run 42426715134 success, no queued/in-progress among first 8 returned). No image pixel analysis or individual 33MB log segments performed; no raw game assets exported, no CI, Unity, APK, shader or game code modified. No trial build vote change (T3 'لا يحتاج' pending actual visual fix).
Next: extract **bounded timestamped raw-log excerpts** around 1793905447216 world_loaded and 1793905695709 death for specific render/asset warnings; then inspect four pinned CL screenshots and correlate ParticleSystemRenderer/Shader/texture identities from authenticated original ZIP2. Avoid unscoped log downloads or unsupported visual causal claims.
