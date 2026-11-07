# T1 — 20261107T1610Z-T1-scheduled-bounded-logline-c7d2
origin: scheduled
resumed_from: 20261107T1515Z-T1-scheduled-logcat-order-6f2c
baseline_sha: 548905d9090630dc0799daeba23aac9917a1ea7c
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; world/save/reopen on owner device from artifact 42058825739 is confirmed; publishing failed; APK86 older.
scope: prompt/coordination/work/WATER-001/T1-20261107T1610Z-T1-scheduled-bounded-logline-c7d2.json
hypothesis: Python iteration over a 500 MB accepted log can allocate an entire malformed physical line before the 32768-byte rejection; a split oversized line must never create a fake second Logcat record.
result: changed scripts/t1_water_logcat_first_roots.py to use readline(32769) and consume oversized physical-line remainder; added test_oversized_physical_line_tail_never_classified. Corrected previous chronological regression fixture's escaped literal backslash-n separators into real newline escapes.
commits: scope 379e8ffdcfb35d812c10e3d3454eccdcfd70aa3b; code 197f89165d06e658ea3514118ff4e5e660647b38; tests 0f8e2b4, a03d2568, 2511a044d65d926f6cb9d8ebb478ee5f99a9f7f7.
validation: source-level review and test fixture review. Full tests NOT EXECUTED: local container DNS cannot resolve raw.githubusercontent.com; no Unity/Android/GPU run. No native build requested. No original CL data acquired. No evidence of restored FFT or FindKernel/Dispatch.
other scopes: T4 physical mouse; T5 buttons and Resolution untouched. Trial vote T1 no-needs remains unchanged; no consensus.
next: execute python3 -m unittest tests.test_t1_water_logcat_first_roots in a checkout, then run against pinned CL session logs and compare totals; investigate authentic Unity kernel index 6 and paired Vulkan/Unity FFT trace, preserving source hashes.
readiness: WATER-001 OPEN; NOT_READY 0/3.
