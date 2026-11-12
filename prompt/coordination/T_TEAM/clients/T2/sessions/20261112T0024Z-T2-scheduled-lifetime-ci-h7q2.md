# T2 scheduled 20261112T0024Z-T2-scheduled-lifetime-ci-h7q2
origin: scheduled
baseline_sha: e58cf4ea3dccf3b2fbe390f768abe267a14da32b
work: prompt/coordination/T_TEAM/work/20261112T0024Z-T2-scheduled-lifetime-ci-h7q2.md
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md

## Read first
Owner confirmed entering, saving, exiting and re-entering world on phone from 42058825739 artifact; packaging publish failed. Device logs contain 23,884 water pass errors and 3,850 FFT kernel errors in 220911-559; later 230108-327 contains 39,132 pass and 6,026 kernel errors. These are historic pinned observations, not a new device test.

## Change
Extend existing T2 source-only workflow to execute both RT pair and RT lifetime Python regression suites; add path triggers for lifetime gate and tests. Preserve checkout SHA, no LFS, concurrency cancel-in-progress:false, timeout and source-only evidence boundary.

## Live branch and Actions
Baseline e58cf4ea3dccf3b2fbe390f768abe267a14da32b; W1 material lineage 43126938128 and GT AssetRipper 43126735391 were in progress when checked. No Unity or APK job requested. Earlier pair CI 43067879594 passed on older c7f042d4 and does not cover the newer lifetime suite.

## Verification limits / next
Publishing the workflow does not prove CI success. Check workflow run on resulting commit, inspect test failures if any. Then prioritize a genuine Unity RT identity/lifetime producer and original Foam pass0/pass1 CB0/sampler/ShaderLab mapping with T1/T3; use T5 unified lab if device evidence is necessary. WATER-001 OPEN, NOT_READY 0/3. Do not touch T4 mouse or T5 Resolution implementation.
