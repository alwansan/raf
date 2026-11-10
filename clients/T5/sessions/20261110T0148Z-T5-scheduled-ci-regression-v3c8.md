# T5 scheduled checkpoint — 20261110T0148Z-T5-scheduled-ci-regression-v3c8
origin=scheduled
resumed_from_sessions=20261110T0049Z-T5-scheduled-staging-regression-k8d2; 20261109T2248Z-T5-scheduled-runtime-attest-6e2c
base_sha=8b024174edc797653a3d607b2294069de234166c
scope_commit=25470b9fdf04812f92696e9789356b986bf7afa1
scope=prompt/coordination/T_TEAM/work/20261110T0148Z-T5-scheduled-ci-regression-v3c8.md

## Confirmed evidence
- Owner device feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: world/save/re-entry confirmed only for 42058825739.
- Earlier source-only staging CI 42715257589 FAILED; newer original Android local startup integration CI 42723946943 SUCCESS at 2026-11-09 23:52 UTC. Different workflows; no proof of final Unity Editor staging.
- T4 physical mouse capture source CI 42723947226 and immersive bars source CI 42723947160 SUCCESS; not phone acceptance.
- Full native run 42696228231 failed before Unity Editor, with no new signed APK/OBB.
- Inspected branch SHA 8b024174edc797653a3d607b2294069de234166c. No duplicate Unity run started.
- Six staging regression tests introduced by f088ec9 have no execution result confirmed in this cycle.

## Limits and next
Only independent CI comparison and coordination records changed. No APK/OBB binary for hashes, matched LogRaft manifest, or phone instrumentation; performance and GUID remain pending. T4 owns mouse capture; Settings/right-side controls not modified.
Next: run python -m unittest discover -s tests -p test_t5_runtime_staging_bytes.py -v with source checkout; inspect new parity CI, coordinate right-side controls and Resolution, verify signed APK/OBB manifest and same-scene LogRaft p50/p95. GPU unavailable must be labelled.
Readiness=NOT_READY.
