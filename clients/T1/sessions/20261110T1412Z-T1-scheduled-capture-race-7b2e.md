# T1 scheduled session — 20261110T1412Z-T1-scheduled-capture-race-7b2e
origin: scheduled
baseline_sha: 019bc6e7d4c90efaad6d7b8cd7a349f6f3cbc68d
scope_commit: a04943f8cd901456050e379e4edb2887a6e2be91
code_commits: d7102e88c3fcaa155584a582e575d56757aadc55, ec4be57b233e94f5a06679131a120627690241de
status: SOURCE_CHANGED / TEST_PENDING / WATER-001 OPEN / NOT_READY 0/3

## Owner evidence read first
docs/DEVICE_FEEDBACK_42058825739_AR.md: phone entered/saved/reentered world from artifact of run 42058825739; package publishing failed. CL 220911-559 23884 water pass and 3850 kernel errors; 230108-327 39132 water and 6026 kernel errors. Distinct sessions; not a single fault count. Later 8 November device log has additional evidence, but cannot substitute original Unity FFT kernel binding.

## Live checks
HEAD initially 019bc6e7d4c90efaad6d7b8cd7a349f6f3cbc68d. Latest visible Actions 42819012779 and 42818996633 completed success on older SHAs, T5 integration tests, not FFT GPU evidence. No pending/running in first page. No redundant CI launched. Existing T4/T5 work untouched.

## Engineering
Inspected scripts/t1_fft_capture_integrity_gate.py. Its pre-open path stat plus post-read size allowed replacement with an equal-size file between stat and open, even when the file's digest matched; could undermine capture identity and hardlink rejection. Added os.open pinned descriptor, pre/post fstat identity/size/mtime checks, and final path identity verification. Added synthetic deterministic swap-before-open regression in tests/test_t1_fft_capture_race.py. Does not disclose private captures. Existing scripts/t1_fft_readback_provenance.py remains unchanged.

## Verification and limitations
Connector accepted both commits. Tests NOT RUN: container git network DNS cannot resolve github.com, and no equivalent CI should be duplicated before coordination. Source change does not prove Unity FindKernel/Dispatch, Vulkan numeric parity, or on-phone water. No XAPK or Unity build launched.

## Next
Execute `python -m unittest tests.test_t1_fft_capture_race tests.test_t1_fft_capture_integrity_gate` on a checkout containing ec4be57b. Check SHA of current HEAD, review concurrent scope and run only a nonduplicate targeted CI if needed. Obtain same-build authentic Unity/Vulkan GPU readbacks and original compute resource GUID/kernel IDs; compare first divergent FFT pass. Keep T4 mouse and T5 resolution/buttons delegated and touch-layout deferred.
