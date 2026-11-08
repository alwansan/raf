# T5 checkpoint 20261108T0650Z-T5-scheduled-ci-provenance-91ac
origin: scheduled
base_sha: 088add0064699eb1d52d631f7e2174f293439b4a
resumed_from_sessions:
- 20261108T0445Z-T5-scheduled-fps-package-7b2e
- earlier T5 scheduled and chat source-only LogRaft provenance checks
work: work/T5/20261108T0650Z-T5-scheduled-ci-provenance-91ac.md
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md
scope: PERF-007 source-only CI verification, no shared Unity resource

## Verified result
- GitHub Actions https://github.com/alwansan/raf/actions/runs/42452502335 completed **success** on immutable head_sha aa2d6c3c84418847e93e970d68299a66490e39e7 at 2026-11-08T05:53:35Z.
- Job source-only-regression success. Both 'Run isolated real parser and CLI regression tests' and 'Verify LogRaft CLI native provenance and legacy compatibility' steps success. This closes prior waiting_ci for this run and establishes source-only regression coverage for native quality/package checks.
- Current branch baseline before this work: 088add0064699eb1d52d631f7e2174f293439b4a. Do not equate newer HEAD with the tested SHA.
- Other observed recent runs: T1 paired FFT diagnostics 42453584790 and 42453577376 failed; T2 Foam JSON ingress 42454485052 success; compatibility guard 42454484959 success. These are separate experiments and not modified.
- Trial votes round trial-20261106-r1: T1/T2/T3/T5 'لا يحتاج', T4 'يحتاج'; consensus absent. No Unity build requested.

## Boundaries
- Source CI does not verify actual phone FPS, GPU time, mouse, right-side buttons, Resolution or APK/OBB binary identity.
- Owner's world/save/reentry success remains tied to run 42058825739 artifact. The phone package binary SHA is unproven.
- Native LogRaft SurfaceFlinger presented_fps_estimate is not Unity FPS. Do not compare without package, scene, resolution and interval provenance.
- No change to T4 physical mouse or any Unity native request, no release or device claims.

## Next
1. Investigate exact APK/OBB manifest/hash pairing for run 42058825739 using preserved signed checkpoint; do not infer device-installed hash.
2. Inspect T5 right-side buttons and Resolution existing implementation against screenshot safe-area requirements; avoid conflicting T5 chat work.
3. For CL pinned 520c4cf4, compare provenance fields and scene boundaries before deriving comparable FPS; report p50/p95 only on valid samples.
