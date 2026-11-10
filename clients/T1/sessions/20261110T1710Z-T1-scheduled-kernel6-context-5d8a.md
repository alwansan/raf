# T1 scheduled session — 20261110T1710Z-T1-scheduled-kernel6-context-5d8a
origin=scheduled
status=SOURCE_CHANGED / TEST_PENDING / WATER-001 OPEN / NOT_READY 0/3
baseline_sha=fd8a4ef2f79bf04e083da6163bdfaebff2869306
scope_commit=e56a9c0f101cac04a8596a50e76a796dbe2e25df
code_commits=ebb1ad498ac663f71155d7dd1698d5cd43e10ab8,570325bff831380aa1085485d2870ec2cd77b7ee
test_commit=64b32f37140a11c52fa1cc2fabb67a8db0d32112
experiment_key=T1-KERNEL6-RAW-CONTEXT-20261110

## Owner/device evidence first
Read docs/DEVICE_FEEDBACK_42058825739_AR.md. Run 42058825739 artifact enabled world entry/save/re-entry on POCO F5 Pro; package publish failed. CL 220911-559: 23884 water pass and 3850 FFT kernel error messages; 230108-327: 39132 pass and 6026 kernel messages. Later 8-Nov CL session: 74359 pass and 11165 kernel messages. Do not combine sessions or claim index 6 is the sixth FFT program. Physical mouse click/wheel remains T4; three buttons/resolution T5. Touch layout deferred.

## Work
Read latest T1 1412Z session and capture integrity tool, owner 8-Nov lab feedback, current team instructions and HEAD. Implemented scripts/t1_kernel6_log_context.py: bounded read-only streaming raw log marker/context extraction, SHA256 source fingerprint, explicit session ID, separate counters, capped samples, marker-only JSON (no proprietary raw lines), no inference of original kernel binding. Added tests/test_t1_kernel6_log_context.py synthetic cases for separate hit counting, cap and unsafe session rejection. Corrected regex escaping in a follow-up commit after reading back GitHub file.

## Verification / limits
GitHub accepted code/test commits; tests NOT RUN because local container cannot resolve github.com to obtain repository checkout. No equivalent Actions dispatched; no Unity/GPU/device claims. Tool is a diagnostic prerequisite, not original resource/FindKernel/Dispatch proof. No shared files or CI resources modified.

## Next
On a checkout containing 64b32f3 run `python -m unittest tests.test_t1_kernel6_log_context`. Run script locally against each raw CL session log separately, with --session matching source; preserve input SHA and first-hit line numbers. Extract original ComputeShader GUID and kernel names from authenticated ZIP2/Unity resource mapping, then instrument same-build FindKernel/Dispatch and compare Vulkan/Unity readbacks from first divergent pass. Do not publish raw CL logs or game assets.
