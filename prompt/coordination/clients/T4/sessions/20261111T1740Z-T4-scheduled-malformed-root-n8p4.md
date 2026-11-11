# T4 scheduled checkpoint
session_id: 20261111T1740Z-T4-scheduled-malformed-root-n8p4
origin: scheduled
resumed_from: 20261111T1636Z-T4-scheduled-sparse-growth-b7q4
baseline_sha: 408fdce57133ee7bff3d12609b3136d1e2690845
scope_commit: b8e9ed33ae2291c55fc6764f2b61e54dca63fc1e
source_commit: 230bd26aca1bd6921d85bdbba4c42d9d0a7a728e
tests_commit: 416f51dbfc6021669b02e60b7e60aebe6a3e4fb0
issue: INPUT-005 OPEN
result: classify() now handles non-object JSON root (null, array, string, number) by emitting invalid_counter_evidence instead of AttributeError. Added four subcases in one unittest method. Source-only regression, not device mouse repair.
verification: GitHub file updates accepted; local git ls-remote failed due DNS unable to resolve github.com, so Python tests and Unity/device not executed this run. No duplicate CI started.
owner_acceptance: Artifact 42058825739 entered local world, saved, exited and re-entered .rgd on phone; packaging failure is separate. Keep keyboard, save format, audio and Settings unchanged.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md and CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57
scope: prompt/coordination/clients/T4/work/INPUT-005/20261111T1740Z-T4-scheduled-malformed-root-n8p4.md
next: run tests/test_t4_capture_gap_classifier.py; analyze same-build Android physical mouse callbacks and Unity legacy reader logs; implement LEFT/RIGHT/MIDDLE/scroll routing and menu/game pointer capture without breaking keyboard. T5 owns Resolution and visible buttons. Do not claim gameplay success from counters.
