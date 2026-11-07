# T2 — Foam per-pass producer correlation boundary
- session_id: 20261107T0215Z-T2-scheduled-pass-role-correlation-a7e4
- origin: scheduled
- base_sha: 1733498f85e74f093f474645ea0d7f69244fe407
- scope_commit: db51cfd0ed1cd948ee6badd84f0ebb4336ed932d
- issue_id: WATER-001 OPEN
- work: prompt/coordination/work/WATER-001/20261107T0215Z-T2-scheduled-pass-role-correlation-a7e4.json
- resumed_from: 20261107T2227Z-T2-chat-blit-texture-role-6c52; 20261107T0117Z-T2-scheduled-pass1-evidence-gate-f3c8

## Owner evidence first
Read docs/DEVICE_FEEDBACK_42058825739_AR.md. Owner entered, saved and reopened world using 42058825739 artifact; publish step failed. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57: 23,884 water-pass and 3,850 FFT errors in one logger session. This supersedes APK86 failure, but is not water success.

## Verified existing evidence and independent result
GitHub HEAD was 1733498f85e74f093f474645ea0d7f69244fe407 before reservation, then db51cfd0ed1cd948ee6badd84f0ebb4336ed932d after isolated scope publication. T2 original CI42305522855 SUCCESS on 681c239c; source producer totals: Texture=0, RenderTexture=1, UNKNOWN=1; destination RenderTexture=1, NULL=0, UNKNOWN=1. Both passes 0 and 1 occur exactly once. These totals DO NOT establish which pass owns either RenderTexture or whether source and destination are paired. There are four possible pass-assignment combinations for the two known roles. Any claim that pass0 has both known roles or that pass1 is fully unknown is unjustified from aggregates alone.

Independently implemented a local source-free schema checker prototype and six unittest cases (6/6 passed) to verify a per-pass 2-row matrix with source/destination roles, reject duplicate/missing pass, invalid role, leaked extra fields, and conservation violations. This prototype is NOT committed to repo and has NOT been tested against original artifact; its tests only establish contract feasibility. Existing T2 chat owns the source scanner, so no competing edit or CI was started. T3 source-only CI42318375479 SUCCESS; do not infer Unity or phone rendering.

## Next engineering action
In a separate T2-owned privacy-safe consumer, accept only two per-pass rows (pass=0 and pass=1), each with source Texture/RenderTexture/UNKNOWN and destination RenderTexture/NULL/UNKNOWN. Require original aggregate conservation, reject duplicate JSON keys, booleans in integer counts, unknown keys and all path/IL/name data. Obtain per-site pass association from pinned private original analysis; until then mark BOTH correlations unresolved. Do not bind ShaderLab, CB0 or texture identities from aggregate counts. Coordinate T1 FFT and T3 FX. No changes to game, .meta, GUID, .rgd, audio, Settings or touch. Trial vote remains لا يحتاج; WATER-001 OPEN; NOT_READY 0/3.
