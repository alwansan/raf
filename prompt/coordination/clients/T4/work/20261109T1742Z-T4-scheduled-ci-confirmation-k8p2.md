# T4 work — CI closure (2026-11-09 17:42 UTC)

- session_id: 20261109T1742Z-T4-scheduled-k8p2
- origin: scheduled
- scope: source-only verification of T4 capture gate CI; no edits to game, T5 UI or shared status.
- base HEAD: 5856423816e17d9cab5212ddd9a3cbe0ed759461
- experiment_key: INPUT-005/T4/capture-gate-runtime-ci
- shared_resource: none (existing completed Actions run only).
- hypothesis: previously waiting eight regressions now have a completed run; avoid duplicating CI.
- evidence: run 42657857161 completed success at source SHA 1648b33fb002fec75f68349914b61f63e2809c36, created 2026-11-09T16:44:48Z. This is source-only and does NOT prove mouse clicks/scroll in Unity.
- preserved: owner-confirmed local world/save/reopen on Artifact 42058825739; keyboard, .rgd, audio, Settings untouched.
- next: correlate captured=true mouse button/scroll callbacks with Unity Legacy Input and on-device Raft response; coordinate T5 for unified lab and Resolution.
