# T1 scheduled session — 20261110T1912Z-T1-scheduled-kernel6-sampling-a6c9
origin=scheduled
status=SOURCE_CHANGED / TEST_PENDING / WATER-001 OPEN / NOT_READY 0/3
baseline_sha=72027bb9e8fa80235332fa57c6140a0781ea812c
current_head_before_session=ae1e60391fc8042a193e75b0a336ec50944fc811
scope_commit=fde538b0080aeb3268fd820538aa919e519fabb1
code_commit=fae16ec685490eeec1de05748fb7fedded8a8bbd
test_commit=ae1e60391fc8042a193e75b0a336ec50944fc811
experiment_key=T1-KERNEL6-ERROR-FIRST-SAMPLING-20261110

## Device evidence and priority
Read docs/DEVICE_FEEDBACK_42058825739_AR.md before changes. Owner successfully entered, saved, exited, re-entered world using run 42058825739 Artifact; packaging publish failed. CL 220911-559: 23884 water-pass and 3850 kernel errors; 230108-327: 39132 and 6026. Separate sessions; no original kernel identity proven. T4 owns physical mouse click/wheel, T5 owns three right-side buttons and Resolution. Unified mini lab policy supersedes separate APKs.

## Actual change
Existing bounded scan selected first N kernel-6 mentions, including benign FindKernel/Dispatch mentions. Added optional errors_only filter for sampled contexts while preserving full legacy counters and SHA provenance. CLI --errors-only. Added synthetic regression proving first two benign mentions do not consume one available error sample. No proprietary logs copied.

## Verification / limitations
Connector confirmed commits on writable branch; no CI or Python test executed in this session. No GPU/Unity/phone execution, original FindKernel binding, or numeric FFT equivalence claimed. No duplicate Actions dispatched; latest observed run 42879360100 failure and 42868458865 success on older SHA. CL read-only. The new switch is opt-in and defaults to old behavior.

## Next
Run python -m unittest tests.test_t1_kernel6_log_context on SHA including ae1e603. Apply --errors-only separately to each authenticated CL raw log with explicit session ID, compare error-context first hits, and resolve original ComputeShader GUID/kernel names from verified ZIP2. Then same-build Unity/Vulkan readbacks and FindKernel/Dispatch instrumented proof. Keep WATER-001 OPEN.
