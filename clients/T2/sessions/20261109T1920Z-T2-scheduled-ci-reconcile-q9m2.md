# T2 scheduled checkpoint — 2026-11-09 19:20 UTC
session_id: 20261109T1920Z-T2-scheduled-ci-reconcile-q9m2
origin: scheduled
base_sha: df2ea73c3d823232a4446b5f968a594ee07098f2
scope_commit: ca4145e8e085378c38fa272214b9cbdf5c0bb0ff
work: work/experiments/20261109T1920Z-T2-scheduled-ci-reconcile-q9m2.md
resumed_from_sessions: 20261109T1818Z-T2-scheduled-r7q2; T2 chat 20261109T1916Z-T2-chat-foam-constant-branch-p8v6

Read device feedback 42058825739, AGENTS.md, owner requirements, STATUS, T_TEAM operating protocol and prior T2 checkpoints. Checked HEAD and active workflows. The previous Foam ABI run https://github.com/alwansan/raf/actions/runs/42673027759 is FAILURE, not queued; jobs API returned zero jobs, so no diagnosis of the exact failing step. The later authenticated-original Cecil run https://github.com/alwansan/raf/actions/runs/42681948189 is SUCCESS at cc4e2519 but is a different workflow. Source on current HEAD shows copied original table rows and a source-isolation regression test; cannot infer ABI test success from the other workflow.

Result: isolated evidence discrepancy in work file; did not dispatch duplicate CI or touch original shaders, assets, mouse, Resolution or T3 work. No Unity/device acceptance. WATER-001 OPEN NOT_READY. Next: run dedicated Foam ABI regression suite on a pinned SHA, retrieve step-level outcome, then cross-pass real texture identity/CB0/ShaderLab evidence. Do not mistake original constant-branch static feasibility for runtime null or device pixels.
