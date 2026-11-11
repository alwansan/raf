# T1 WATER-001 — CI contract repair
origin: scheduled
session_id: 20261111T1815Z-T1-scheduled-chronology-ci-contract-b72e
base_head: 281a770541aec0484842f2429b253f96600372c3
scope: .github/workflows/raft-t1-water-startup-order.yml only, plus independent T1 session and work records
experiment_key: t1-cl-chronology-cli-schema-20261111
shared_resource: none; no Unity, GPU, APK or CL writes
hypothesis: CI43066215281 failed because workflow passes obsolete --session/--source-commit flags to positional-only t1_water_startup_order.py, and then expects a legacy JSON schema. Preserve pinned CL SHA256 and compare current analyzer output with authentic summary.
evidence: https://github.com/alwansan/raf/actions/runs/43066215281 (5/5 synthetic PASS; CLI exit 2); owner https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md
peer scope: T4 physical mouse, T5 resolution and packaging, T2 Foam; no overlap.
taken_over_from: T1 prior session 20261111T1712Z-T1-scheduled-preworld-order-93ac; B historical source only, no agents reactivated.
status: scope recorded before workflow modification.
