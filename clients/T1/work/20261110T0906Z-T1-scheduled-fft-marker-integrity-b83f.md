# T1 isolated scope — 20261110T0906Z-T1-scheduled-fft-marker-integrity-b83f
origin: scheduled
issue_id: WATER-001
status: active
base_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; source e9c358eda01785b65e4eb14f18723da426635628
resumed_from_session: 20261110T0814Z-T1-scheduled-fft-multipair-a6c9
intended_files: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_native_trace_contract.py; clients/T1/sessions/20261110T0906Z-T1-scheduled-fft-marker-integrity-b83f.md; this work file
hypothesis: A native AFTER/THREW trace can currently include contradictory source/GPU mapping flags not validated, producing a misleading positive managed pair. Reject false verified flags without claiming GPU proof.
experiment_key: T1-fft-native-terminal-evidence-flags-v1-8aa32937d423
resource_key: none (Python metadata-only)
shared_file_ownership: T1 script and T1 test only; no Unity/OBB/CL modifications.
readiness: WATER-001 OPEN / NOT_READY; synthetic and managed returns are not native GPU proof.
