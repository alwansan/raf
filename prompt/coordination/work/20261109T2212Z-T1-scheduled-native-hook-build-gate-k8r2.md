# T1 WATER-001 — native FFT trace deployment dependency
session_id: 20261109T2212Z-T1-scheduled-native-hook-build-gate-k8r2
origin: scheduled
issue_id: WATER-001
status: completed (read-only diagnosis)
base_sha: 19bf77c3423e87c80479bc62e14e86e91c6560b2
intended_files: this work file; independent T1 session checkpoint only
experiment_key: full-native-42696228231-reconstruct-attestation-preunity-fft-trace-blocker
resource_key: none (read-only Actions log; no Unity or APK run)
resumed_from_session: 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
hypothesis: original Dx11FFT thrown/returned Android hook is not testable in latest full native build if reconstruct fails before Unity.
result: CONFIRMED: run 42696228231 reconstruct failed at 'T5 attest final native Android runtime source bytes (read-only)' with ValueError 'Original-managed/native Unity runtime staging drift: managed_only=0 native_only=1'; publish-early-test skipped. No new device build/FFT trace from this run. T5 owns native attestation fix; T1 does not modify overlapping files.
evidence: https://github.com/alwansan/raf/actions/runs/42696228231 ; job 129428944191. Existing T1 source-only success: https://github.com/alwansan/raf/actions/runs/42695722354 and https://github.com/alwansan/raf/actions/runs/42696197130.
next: after T5 attestation is fixed and a separately authorized full build succeeds, capture same-build raw Android original FFT JSONL; correlate before/returned/threw with index6 and first water pass, then compare authentic GPU output. No duplicate CI triggered.
