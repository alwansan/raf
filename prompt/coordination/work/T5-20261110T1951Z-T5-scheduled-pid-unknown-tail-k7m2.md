# T5 PERF-007 scope 20261110T1951Z-T5-scheduled-pid-unknown-tail-k7m2
origin=scheduled; branch=feature/android-native-port; baseline=02a942edb9d940fe468e703597136f86be71f971

Owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; device success on artifact 42058825739 only. The latest historical CI 42868458735 failed three startup-prefix tests; production prefix fix f5a29e49c521b2eb46af486d951b131a8011afd4 is present at current HEAD. This work does not claim new phone measurements.

Scope: isolated PERF-007 source-only process epoch regression; files tests/test_t5_cl_pid_startup_prefix_real_gate.py and this work/session file. Hypothesis: after verified running PID, a later unknown process state MUST remain a boundary even if next verified sample reuses the same numeric PID; this complements startup-prefix exception and prevents FPS mixing. Experiment key T5-PERF007-UNKNOWN-TAIL-20261110. No Unity resource; no changes to T4 mouse, T5 UI/Resolution, APK/OBB, shared state, or CL. Do not duplicate active Actions.

Next: add regression and verify through existing narrow workflow, record outcome. No real device/GPU inference.
