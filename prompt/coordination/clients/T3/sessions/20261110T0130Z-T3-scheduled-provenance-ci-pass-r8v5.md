# T3 — verified smoke34 provenance regression
session_id: 20261110T0130Z-T3-scheduled-provenance-ci-pass-r8v5
origin: scheduled
resumed_from_sessions: 20261110T0029Z-T3-scheduled-provenance-ci-h6q2; 20261109T2332Z-T3-scheduled-spv-location-bound-f4k9; 20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2
base_sha: 7b9d290d69a65c41bdc1c5f7b738157a4a476a79
scope_commit: a56f6b452af79cb4fd470197d0928994313530a2
work: prompt/coordination/work/RENDER-002/20261110T0130Z-T3-scheduled-provenance-ci-pass-r8v5.md
status: source_regression_verified; RENDER-002 OPEN; NOT_READY 0/3

## Live verification 2026-11-10 01:30 UTC
Read owner device feedback and T3 prior checkpoint. GitHub Actions run https://github.com/alwansan/raf/actions/runs/42728727179 completed SUCCESS for source commit 80f4c4d27f6dee329d4a548df592b73beabfcd2b, closing prior waiting_ci for the 14 synthetic provenance tests. The same commit's runner compatibility check 42728726420 also succeeded. No new CI dispatched, no Unity or APK build. Latest observed branch HEAD 7b9d290d69a65c41bdc1c5f7b738157a4a476a79. CL test directory contains newer 20261109 uploads, but no claim of successful smoke pixel repair from them.

## Technical boundary
The gate verifies uniqueness, coverage, uint32 locations and allowed unused declared lanes; it does not authenticate the mapping between original DXBC input lanes and SPIR-V locations. Prior 22/28 lane evidence remains a component-count observation, not an instruction-proven semantic map. Source-only success cannot prove Blend/Alpha or fix white raft/hand, square smoke, fire or water on Android. Owner's 42058825739 world/save/reentry success is preserved; no regression claimed.

## Next
Build a bounded private instruction-derived mapping comparison for the original smoke shader (without exporting proprietary bytes), with authenticated ZIP2 pin and SHA; report aggregate mismatch categories and compare actual particle renderer material/ShaderLab blend states. Check current HEAD and overlapping T3 chat work first. Preserve T4 mouse and T5 resolution/UI scopes, audio, Settings, .meta/GUID and .rgd. No fake READY flags.
