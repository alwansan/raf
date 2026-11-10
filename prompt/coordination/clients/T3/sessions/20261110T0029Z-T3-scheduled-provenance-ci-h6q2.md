# T3 — smoke34 provenance CI checkpoint
session_id: 20261110T0029Z-T3-scheduled-provenance-ci-h6q2
origin: scheduled
issue_id: RENDER-002 OPEN; NOT_READY 0/3
resumed_from_sessions: 20261109T2332Z-T3-scheduled-spv-location-bound-f4k9; 20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2
base_sha: 3a7c2cdce27d280d33ffa93e1aa3ce22199cefa5
scope_commit: dbc32710a03590a7aca12dc86fb832f07a1f10c8
workflow_commit: 80f4c4d27f6dee329d4a548df592b73beabfcd2b
work: prompt/coordination/work/RENDER-002/20261110T0029Z-T3-scheduled-provenance-ci-h6q2.md
workflow: .github/workflows/raft-t3-smoke34-provenance-regression.yml
experiment_key: t3-smoke34-provenance-synthetic-unittest-14cases-uint32-boundary-v1
status: waiting_ci

## Verified inputs and action
Read owner device feedback 42058825739: owner succeeded world save/reentry but white hand/raft, square smoke and water errors remain. Read T3 current provenance gate, all 14 source tests and last session. Branch HEAD was 3a7c2cdc; recent 12 Actions completed and no equivalent smoke34 regression running. T4 mouse and T5 UI/resolution are independent scopes.

The 20261109T2332Z location overflow regression was published without test execution. Created isolated source-only Actions workflow to compile gate/tests and run all 14 unittest controls, with checkout pinned to commit, 5-minute limit, no LFS, no Unity, no raw game assets, no cancellation of other jobs. Workflow push trigger limited to its own file; no repeated build or heavy CI dispatch.

## Checkpoint / limits
After workflow commit, the Actions listing did not yet show the new run. Do not claim PASS; recheck the workflow by name and commit 80f4c4d27 before dispatching. Source-only structural validator cannot prove authentic DXBC→SPIR-V semantic provenance or correct Blend/Alpha, white materials or smoke pixels. Prior CI 42696526193 is older source, not validation of latest bounds change. Preserve game resources, .meta/GUID/.rgd, audio and Settings.

Next: read workflow result and logs; if fail fix isolated test/source issue; if pass advance authentic instruction-derived mapping and compare original/export render states. CL screenshots still require device evidence. 
