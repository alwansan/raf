# T1 scheduled checkpoint 20261111T2313Z-T1-scheduled-fft-fixture-6c82
origin: scheduled
resumed_from_sessions: 20261111T2205Z-T1-scheduled-fft-ci-triage-4d8c and prior T1 FFT work
base_sha: dbf9b24e89dc1d90e3958b026e3aea1d20bf34e2
scope_commit: ff879733bfda6bbb594ed11ed1ef923b3f11fba9
fix_commit: b245464af853707acea20bd0d86e31b9685f351c
issue_id: WATER-001

## Verified finding
Read full logs of job 130792235243 in run 43101033840. 14/16 capture-budget suite tests passed, two positive fixtures failed: test_single_small_matching_pass and test_accept_nested_regular_capture. Both supplied the same file path as reference and observed. The production comparator correctly rejects samefile aliasing after fcb0c5c; this was a stale test fixture, not a reason to weaken alias protection. Other FFT comparator suites in the job passed.

## Action
Changed only scripts/test_t1_fft_capture_budget.py positive fixtures to write two separate regular files with identical 16-byte payloads. Both should still be accepted as matching independent captures. No production comparator changes. CI test execution for this commit remains unverified; check fresh workflow run for b245464af853707acea20bd0d86e31b9685f351c before dispatching any duplicate.

## Device and limits
Owner's 42058825739 Artifact proved entering/saving/reentering world, not correct water. CL sessions 220911-559 and 230108-327 show 23,884/39,132 water pass errors and 3,850/6,026 FFT kernel errors respectively. Unity FindKernel/Dispatch original binding and Vulkan/Unity numerical parity remain unproved. No Android or Unity build run in this session. T4 mouse and T5 Resolution/three-button UI scopes untouched.

## Next
Confirm fixture tests via CI on the new SHA; if green, return to original FFT .compute/.meta/GUID and FindKernel/Dispatch trace capture, and first numeric divergence with independent Vulkan and Unity captures. Preserve source authenticity and avoid publishing raw game assets.
