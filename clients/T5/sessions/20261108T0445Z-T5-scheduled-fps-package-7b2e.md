# T5 scheduled session 20261108T0445Z-T5-scheduled-fps-package-7b2e
origin: scheduled
baseline_sha: be2a7065144e9300a8932dba278838636ba27789
work: work/T5/20261108T0445Z-T5-scheduled-fps-package-7b2e.md
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md
scope: LogRaft presented FPS package provenance only; no Unity shared resource.

## Verified changes
- d58d981bf0dd7af46bdf419b6e55cdf7d3da9512: reject native lograf_shell samples carrying an explicit package different from com.alwansan.raft.androidtest; retain legacy flat synthetic inputs without package.
- a20f86d121c1a2fac84f92f32a9d8fecd1007d4d: add regression with one valid Raft sample and one cross-package sample; expected 1 accepted, 1 rejected.
- Last observed HEAD a20f86d121c1a2fac84f92f32a9d8fecd1007d4d.
- No fresh source CI run identified for these commits; source-only change is NOT device validation.

## Context and limits
Owner phone success (world/save/reentry) is only for run 42058825739 artifact; package SHA identity not proven. CL metrics are SurfaceFlinger estimates, not Unity FPS. No new APK/OBB pair identity, no scene-matched performance comparison. T4 owns physical mouse; existing T5 right-safe-area buttons and Resolution source work remains separate and not device-proven. Trial vote is not 5/5; do not dispatch duplicate Unity.

## Next
Run python3 -m unittest tests.test_t5_lograft_presented_fps (or discovery by filename) on checked-out HEAD; confirm CI if available. Cross-check package field presence on pinned CL 520c4cf4 metrics and apply conservative provenance gates. Continue Resolution and right-side device validation in nonoverlapping T5 scope; verify signed APK/OBB manifest before cross-build comparison.
