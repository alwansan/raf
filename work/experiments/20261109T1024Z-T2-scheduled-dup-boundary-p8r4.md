# T2 WATER-001 scope
session_id: 20261109T1024Z-T2-scheduled-dup-boundary-p8r4
origin: scheduled
issue_id: WATER-001
baseline_sha: b3076af45843798950314d654f5bad51fb5f5059
status: active
intended_files: android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs; clients/T2/sessions/20261109T1024Z-T2-scheduled-dup-boundary-p8r4.md; this work file
experiment_key: foam-original-cil-backtrace-dup-underflow-fail-closed-v1
resource_key: none (source-only; no Unity, no private original scan)
hypothesis: DUP with insufficient tracked stack depth must return an explicit unknown reason, not reset depth and continue to an unrelated producer.
taken_over_from: clients/T2/sessions/20261109T0851Z-T2-scheduled-alias-ci-h4q8.md; CI 42589085141 success
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 artifact world/save/re-enter, water FFT errors remain
No shared shader files or T3/T4/T5 scopes. CI latest 42597471313 T5 PNG regression failure; no equivalent T2 jobs running in latest eight.
