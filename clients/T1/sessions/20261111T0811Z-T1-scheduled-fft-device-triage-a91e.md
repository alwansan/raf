# T1 session 20261111T0811Z-T1-scheduled-fft-device-triage-a91e
origin: scheduled
baseline: c6158c26db367ab1dc44ab5c82634fd60eac16fd
scope_commit: 786fbb2857d8c2d02a13819f45e64c7a3e2e3bf7
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (phone test run 42058825739; source e9c358eda01785b65e4eb14f18723da426635628)
CL_snapshot: 520c4cf409aa20a4db54ff80ed87d8807d9cba57
status: WATER-001 OPEN, NOT_READY 0/3

## Confirmed
The owner entered a world, saved, exited and re-entered using the run artifact; package publication failed. This supersedes historical APK86 world-entry failure. Phone evidence lists 23,884 pass / 3,850 FFT errors in 220911-559 and 39,132 pass / 6,026 FFT errors in 230108-327. 57 frame estimates for first log (mean 22.29), only two usable in second; HUD 18.27 FPS and p95 82.82ms is not GPU time. The current branch HEAD at opening was c6158c26db367ab1dc44ab5c82634fd60eac16fd. Latest observed platform-test Actions 42982481448 succeeded on 85fc2a2; this does not validate FFT.

## Quantitative check
Water-pass count increased by 15,248 (+63.84%); FFT count increased by 2,176 (+56.52%). FFT/water-pass count fractions are ~16.12% and ~15.40%. Counts are events, not unique failing kernels, durations, frames or performance rates. Their difference cannot establish worse graphics or different shader identity. The two logs must be segmented by runtime phase and correlated with original kernel map, actual FindKernel name, dispatch groups and shader GUID before causal claims.

## Work performed and boundaries
Reviewed current t1_compare_kernel6_sessions.py and end-to-end test; comparison already explicitly rejects identity/causality inference and duplicates, so did not add another synthetic validation patch. Read owner priority updates for physical mouse (T4) and safe-area buttons/Resolution (T5); T1 did not modify overlapping files. No Unity, GPU, phone test, build or Actions dispatch was launched. The CL raw logs were not downloaded or executed in this run, so no per-event context was established.

## Next
Fetch sanitized logs from the pinned CL snapshot and run existing scan/pipeline tests, compare first actual error in each session, trace resource GUID and kernel names in original ZIP2 compute resources, then instrument FindKernel/Dispatch and compare first numerically divergent FFT pass. Use a separate experiment output and avoid proprietary raw shader publication. Do not call READY.
