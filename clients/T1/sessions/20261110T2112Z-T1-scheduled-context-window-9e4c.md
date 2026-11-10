# T1 scheduled — 20261110T2112Z-T1-scheduled-context-window-9e4c
origin=scheduled
status=SOURCE_CHANGED / TEST_PENDING / WATER-001 OPEN / NOT_READY 0/3
resumed_from=20261110T1912Z-T1-scheduled-kernel6-sampling-a6c9
baseline_sha=df3463b79a87c8720a0363e3dd90aa343b14eef3
scope_commit=9ec65a95fc9b0a8e89702de202cd40bf86f639d5
code_commits=34ba93841fba7bb9ae6b437b4b58b71486b45129,7875bc046addbc83067f6256cbe48b11bb76690b
test_commit=fd023463e1ac0df5cbe31a4631e849ba8d8e1d4d
experiment_key=T1-KERNEL6-TRUE-LINE-WINDOW-20261110-LOG-MARKER-BOUNDARY

## Verified owner baseline
docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered world, saved, exited and re-entered using run 42058825739 Artifact; publishing APK/OBB/XAPK failed. CL 220911-559: 23884 water-pass and 3850 kernel errors; CL 230108-327: 39132 and 6026. Do not equate kernel index 6 with original FFT kernel identity. Current 8 Nov shared mini-lab policy is one APK/team testpack; T4 physical mouse and T5 Resolution/three right-side buttons separate active scopes.

## Source finding and fix
scripts/t1_kernel6_log_context.py previously advanced look-behind deque only on lines with diagnostic markers, so --before=8 could report a FindKernel hundreds of physical lines before a kernel6 error as nearby. Changed deque to advance on every physical line, while exporting only diagnostic markers (no proprietary log payload). Look-ahead already used physical line numbers. Added scripts/test_t1_kernel6_context_window.py with distant marker, nearby marker, zero-before regressions. No raw game data added.

## Verification and limits
Connector confirmed all four writes on feature/android-native-port. Local container curl to raw.githubusercontent.com failed DNS (Could not resolve host); no local Python test or CI run confirmed. No Unity/phone/GPU dispatch and no numeric FFT equivalence. Existing Actions inspected; no equivalent job duplicated. No shared T4/T5 files edited.

## Next
Run `python -m unittest scripts.test_t1_kernel6_context_window` on a checkout at/after 7875bc0 and fd02346. Run the scanner separately on authenticated CL 220911-559 and 230108-327 raw log with --errors-only; inspect actual first physical-window markers. Resolve ComputeShader GUID and real FindKernel/Dispatch mapping from pinned ZIP2, then same-build Vulkan/Unity readback numeric first mismatch. WATER-001 remains OPEN, NOT_READY 0/3.
