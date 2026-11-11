# T1 scheduled session — 2026-11-11T02:17Z
session_id: 20261111T0217Z-T1-scheduled-kernel6-false-positive-4c9a
origin: scheduled
branch: feature/android-native-port
baseline_sha: 983ace0c53611b994ad5d114e082c4495223e56d
final_observed_sha: d8034b57c26fc5dc8fa96d3c9c8ec5d0efe56a5c
work: prompt/coordination/T_TEAM/work/20261111T0217Z-T1-scheduled-kernel6-false-positive-4c9a.md
source_commit: 63911b1209dbea8331a10cdd3e776eb5a6f64758
test_commit: d8034b57c26fc5dc8fa96d3c9c8ec5d0efe56a5c

## Owner evidence and precedence
DEVICE_FEEDBACK_42058825739_AR.md: device world entry, save and re-entry succeeded from artifact, publication failed. Historical APK86 failure is not current device outcome. 220911-559: 23884 water pass errors, 3850 kernel errors; 230108-327: 39132 water pass errors, 6026 kernel errors. Later 8 November shared mini-lab policy and mouse feedback take precedence for relevant scope. No new phone run in this session.

## Result
Inspected current scripts/t1_kernel6_log_context.py and reproduced false positives: 'kernel 6.0' and 'kernel index 6.1' matched integer index 6. Replaced numeric boundary with (?![\\w.]) on bare and prefixed forms. Added independent unittest script scripts/test_t1_kernel6_false_positive_4c9a.py. Standalone Python regex check passed 12 lexical cases locally; repository-import unittest, real CL log analysis, Unity GPU execution, numeric Vulkan/Unity parity and device validation NOT performed. No CI started, no T4/T5 files touched.

## Next
Run python scripts/test_t1_kernel6_false_positive_4c9a.py in repository; compare kernel6 error sample counts on fixed CL logs by session; then map source ComputeShader GUID -> FindKernel name -> actual Dispatch. Do not infer kernel name from index. Continue first divergent FFT pass numeric parity with pinned original data, not synthetic equivalence. Coordinate with T4 mouse and T5 resolution/three buttons rather than duplicate their files. WATER-001 OPEN, NOT_READY 0/3.
