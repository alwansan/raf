# T1 scheduled checkpoint — 20261110T1808Z-T1-scheduled-kernel6-error-classification-f2a7
origin: scheduled
issue: WATER-001
base_sha: 55534e30c8efc54d93f20e68b7980e8a484273aa
scope_commit: 8b52a870fb0b4628ad04d42f0bab42cba1dd0069
implementation_commit: 5355bbcf6661770ac56ec74bbfc870761f6c7c05
regression_commit: 0631eba80b39549904f1fb75e3c16243cda838b4
status: source_changed_unverified
resumed_from: 20261110T1710Z-T1-scheduled-kernel6-context-5d8a; 20261109T2030Z-T1-chat-index6-selector-correlation-c2d7

## Evidence and change
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner's Artifact run 42058825739 entered/saved/reentered world; packaging failed. CL pinned 520c4cf, sessions 220911-559 (23,884 pass/3,850 kernel messages) and 230108-327 (39,132/6,026) are separate. No inference that index6 equals sixth native FFT shader.

Read AGENTS.md, CURRENT_OWNER_REQUIREMENTS.md, STATUS.md and T_TEAM coordination. Latest source head at opening 55534e30c8efc54d93f20e68b7980e8a484273aa. Actions 42868458865 runner guard succeeded on prior 3bc2668; not a Unity GPU test. T4 owns pointer capture/buttons, T5 owns Resolution and delivery; no overlap.

scripts/t1_kernel6_log_context.py previously counted any line containing kernel 6 as a kernel-error message, even benign FindKernel/Dispatch mentions. Added two separate counters kernel6_error_lines and kernel6_nonerror_mentions while preserving historical kernel6_lines; error classification is deliberately conservative (same-line error keyword), not proof of causality. Added two isolated regression fixtures in tests/test_t1_kernel6_error_classification.py. These source changes have NOT been executed in CI or locally; container network cannot resolve raw.githubusercontent.com. Do not claim tests passed. No device test, original GPU binding, numeric divergence, or APK build.

## Next
Run python -m unittest discover -s tests -p 'test_t1_kernel6_error_classification.py' on a checkout including 0631eba8, then apply script to each CL session separately with source SHA. Investigate actual Unity FindKernel/Dispatch resource/GUID and FFTsize/bank before claiming kernel6 identity; compare Vulkan and Unity readbacks from same immutable build. WATER-001 OPEN / NOT_READY 0/3.
