# T1 scheduled session — 2026-11-09 16:10 UTC

session_id: 20261109T1610Z-T1-scheduled-duplicate-pair-8f31
origin: scheduled
baseline_head: 2a1496903c3f4a354638ba56b8991f4d8b5b8523

## Owner and baseline
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first: owner verified world enter/save/re-enter on Artifact of run 42058825739, not on a release. Water-pass errors 23,884/39,132 and FFT kernel errors 3,850/6,026 are separate phone sessions; do not aggregate. Artifact packaging failed. Newer shared mini-lab policy dated Nov 8 supersedes separate labs. T4 owns physical mouse click/scroll/pointer capture; T5 owns Resolution/UI and package checks.

## Work
Independent scope: clients/T1/work/20261109T1610Z-T1-scheduled-duplicate-pair-8f31.md. Identified a trace accounting flaw: duplicate BEFORE/AFTER events produced duplicate_event error yet previously paired_count could remain nonzero or a later return could pair a duplicated BEFORE. Implemented fail-closed invalid_sequences accounting without changing runtime/game assets.

Source commit: 7d9f8dfbacff18245d70623a96138b113c2e36ed
Regression commit: 887fb713d1e16befc0dffbd15b02f927055dc3bb
Tests: scripts/test_t1_fft_duplicate_pair_regression.py (four cases). Tests are committed but not yet executed; local GitHub DNS is unavailable and no CI was launched. This is trace bookkeeping only, not proof of FindKernel, Dispatch, original resource binding, GPU execution or numeric Vulkan/Unity parity.

## Next
Run python -m unittest discover -s scripts -p 'test_t1_fft_duplicate_pair_regression.py' in a checked-out branch or a cheap existing CI workflow. Then inspect real owner CL logs and compare original shader GUID/kernel names with Unity runtime before claiming any water repair. WATER-001 OPEN / NOT_READY. No game build triggered; no shared file or team scope modified.
