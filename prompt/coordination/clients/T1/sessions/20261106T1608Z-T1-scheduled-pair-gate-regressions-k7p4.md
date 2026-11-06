# T1 scheduled — paired FFT gate synthetic regressions

- session_id: 20261106T1608Z-T1-scheduled-pair-gate-regressions-k7p4
- origin: scheduled
- resumed_from_sessions: 20261106T1408Z-T1-scheduled-pair-input-readiness-v3; 20261106T1310Z-T1-scheduled-ulp32-m4q8
- branch: feature/android-native-port
- scope_commit: c58874d5fd3a059204bdf817a16840dddec86f43
- test_commit: 20ad8d51c259f3c39b6ffa0926b778c00c699bd3
- test_correction_commit: 55f6e242416fa1b723aad1ec7c77d28276540325
- origin_reference: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- work: prompt/coordination/work/WATER-001/20261106T1608Z-T1-scheduled-pair-gate-regressions-k7p4.json

## Owner evidence first
docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered, saved, exited, reentered world from run 42058825739 artifact; publishing failed. CL pinned 520c4cf sessions: 220911-559 23884 water pass errors/3850 FFT kernel errors; 230108-327 39132/6026. This is newer than APK86. T4 physical mouse; T5 buttons and Resolution; do not alter their files.

## Distinct engineering step
Added ten source-free synthetic regression cases for existing `scripts/t1_fft_invocation_pair_gate.py`, using a bounded 3-site invocation trace fixture with SHA256-bound capture bytes. Covers accepted matching traces with explicit unsigned/not-authenticated result, coordinate divergence, trace digest tampering, input/dispatch mismatches, same underlying file, wrong and boolean site coverage, duplicate JSON keys, and truncated capture. No proprietary data or GPU job. Fixed fixture padding after reviewing committed content.

Run from repository root:
`python -m unittest discover -s tests -p 'test_t1_fft_pair_gate_synthetic_k7p4.py' -v`

## Verification and limitations
Tests authored and committed; **not executed on actual repository** in this run (local container github.com DNS unavailable; connector supports file reads/writes but not shell execution). Do not claim passing tests. No original+candidate same-input/same-dispatch traces yet; no measured first Vulkan↔Unity divergence, ULP or Unity FindKernel/Dispatch/device evidence. No CI workflow launched or cancelled. WATER-001 OPEN; NOT_READY 0/3.

## Next
Run tests in suitable existing lightweight CI or accessible checkout without duplicating active jobs. If passing, obtain independently authenticated original/candidate capture pair with identical input and dispatch, feed pair gate, then compare first invocation mismatch. Continue Unity kernel binding only after provenance is established. Do not touch T4/T5 input/Resolution scopes.
