# T5 scheduled — Resolution direct-edge provenance consistency
session_id: 20261111T2053Z-T5-scheduled-edge-consistency-r4k8
origin: scheduled
baseline_sha: fa4956da534c246f05fa9ff30a5e362d2191cd38
resumed_from: 20261111T1848Z-T5-scheduled-graph-bounds-c9e2 (work), 20261111T1748Z-T5-scheduled-resolution-graph-m6q8 (session)
scope: prompt/coordination/T_TEAM/work/20261111T2053Z-T5-scheduled-edge-consistency-r4k8.md
status: source_committed; CI_pending_verification; NOT_READY

## Verified evidence
Read owner device report: run 42058825739 at source e9c358e; owner successfully entered/saved/re-entered world. Source-only Resolution delegate CI 43081428467 completed SUCCESS at 2026-11-11 18:50 UTC on cf2d823; this is not device, prefab binding or render-scale evidence.
Live branch HEAD before work fa4956da534c246f05fa9ff30a5e362d2191cd38, latest T4 captured-input checkpoint. T4 physical mouse ownership preserved. No Unity shared resource requested or duplicate Actions dispatched.

## Change
Original-IL validator now rejects direct same-type Apply calls when internal direct call edge count is zero or smaller than the largest relevant direct-call subset. Regression cases cover both option methods and delegate targets. Source commits 956be1f28ff848a878b0bcb89952baf5ace0bc59 and e4b9bfca1bcd89cbaa2ae035dc667bb08b4d62ed. Scope commit 90187d6b8c1020bba61b058342bda71e8537f975.

## Boundaries and next
Synthetic source-only consistency gate, not proof of original runtime dropdown callback registration. No edits to game Settings, three right buttons, T4 mouse, APK/OBB, or CL. Tests not executed locally; check new CI run on e4b9bfca, or run python -m unittest tests.test_t5_validate_resolution_delegate_probe. Follow original prefab/scene event wiring and Android render-scale persistence separately. For APK/OBB, acquire actual signed bytes and verify manifest/versionCode/OBB SHA; no ungrounded phone FPS attribution. Keep Stay in Chat and NOT_READY 0/3.
