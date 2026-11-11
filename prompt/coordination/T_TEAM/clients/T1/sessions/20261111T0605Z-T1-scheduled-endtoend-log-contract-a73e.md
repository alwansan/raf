# T1 scheduled session — 2026-11-11T06:05Z
session_id: 20261111T0605Z-T1-scheduled-endtoend-log-contract-a73e
origin: scheduled
branch: feature/android-native-port
baseline_sha: acaa8cb0fb661ee69be5ee1273aa970f3b8b465b
work: prompt/coordination/T_TEAM/work/20261111T0605Z-T1-scheduled-endtoend-log-contract-a73e.md
plan_commit: aaba2c4ceb1e07372c66ae98acbb6425ef92d4a3
test_commit: f4d2527608c9933807bfaf50e8df0aa4f57e69ad
latest_checked_sha: f4d2527608c9933807bfaf50e8df0aa4f57e69ad

## Evidence and precedence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first: source e9c358eda01785b65e4eb14f18723da426635628; artifact phone world entry/save/re-entry succeeded; publishing failed. CL fixed 520c4cf409aa20a4db54ff80ed87d8807d9cba57; 220911-559 has 23,884 water pass errors and 3,850 kernel errors; 230108-327 has 39,132 and 6,026. These are report aggregates, not a proved kernel6-to-FFT-asset identity. Read AGENTS and current T_TEAM protocol; 8 Nov unified mini-lab instruction supersedes older separate mini APK policy. Latest observed Actions run 42967944744 completed success for offline integration (not GPU proof).

## Concrete result
Added scripts/test_t1_kernel6_pipeline_endtoend.py to exercise scanner -> sanitized JSON -> cross-session comparator using two distinct synthetic physical-line logs. Checks kernel #6 / (6) recognition, excludes 16 / 6.1, checks proximity bounded by actual filler lines, water counters, error deltas, independent SHA, explicit unproven identity/noncausality and absence of a synthetic private string in emitted JSON. Also checks same bytes under different session names rejected.
No CI launched, no T4/T5 files changed. Git local DNS cannot resolve github.com; repository Python unittest has NOT been executed. Connector created source and HEAD was reread after publication. No phone GPU, FindKernel-to-GUID mapping, Dispatch, numeric Vulkan/Unity parity or water fix claimed.

## Next
Run `python -m unittest discover -s scripts -p 'test_t1_kernel6_pipeline_endtoend.py' -v` in a checkout or existing lightweight CI; if passing, run read-only scanner --errors-only separately on CL logs 220911-559 and 230108-327, then compare sanitized JSON. Identify original FFT ComputeShader asset/GUID and instrument actual FindKernel/Dispatch to bridge numeric first mismatch. Coordinate with T4 physical mouse and T5 Resolution/right controls. WATER-001 OPEN NOT_READY 0/3.
