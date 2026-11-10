# T3 scheduled session — 20261110T0932Z-T3-scheduled-render-state-ci-verified-v6n3
origin: scheduled
baseline_sha: 0ba8582d8e38ae4f2d3db1190aeda41b2bc1818d
scope_commit: 0983cff7da0d81ed7edb531ced7a8f54400ee475
work: prompt/coordination/work/RENDER-002/T3-20261110T0932Z-T3-scheduled-render-state-ci-verified-v6n3.md

## Source and owner requirements
Read AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM/CHAT_AND_SCHEDULE_AR.md, PROMPT_AR.md, OPERATING_MODEL_AR.md, and docs/DEVICE_FEEDBACK_42058825739_AR.md. The November 5 owner phone report confirms world/save/reload only for artifact 42058825739. CL frozen evidence links and screenshot locations are in that report; no new on-device observation made in this cycle. Preserve sound, Settings, GUID, .rgd and game assets. No touch work. T4 owns physical mouse; T5 resolution/layout.

## Restored baseline
Previous scheduled session: 20261110T0828Z-T3-scheduled-render-state-ci-m6q2.md; workflow .github/workflows/raft-t3-render-state-pair-regression.yml at 652a03ec. Read T3 state.json and MEMORY.md; older chat checkpoint on 8 Nov includes shared mini APK device PNG unverified, not proof of restored game materials. Previous T3 original/export same-instance TexEnv parity was 227/227 with 25 external refs unproven (41939404454). Do not infer smoke alpha or white surface root cause from that result.

## Verified new result
GitHub Actions run https://github.com/alwansan/raf/actions/runs/42782959918 finished success; head SHA 652a03ec62ef5ac39d126536d7f8582708ea8c7c, started 2026-11-10 08:28:49 UTC. This resolves the prior waiting_ci state for the render-state comparator tests; it is source-only regression. Most recent checked HEAD 0ba8582d8e38ae4f2d3db1190aeda41b2bc1818d at 09:23 UTC; no active/queued Actions among latest 100 when checked. No duplicate CI, Unity, APK or mini lab build started.

## Status / continuation
RENDER-002 OPEN / NOT_READY 0/3. No original/export Blend/Alpha evidence produced in this cycle. Need a SHA-pinned same-material render-state extraction from original ZIP2 and corresponding actual export, with non-raw safe JSON summaries and provenance; compare alpha blend, zwrite/ztest, color mask, queue and shader keyword variants, then link concrete renderer/prefab to phone CL image. Distinguish source/export proof from Android pixel proof. No game file modifications.
