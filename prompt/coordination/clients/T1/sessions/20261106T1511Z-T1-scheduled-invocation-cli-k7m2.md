# T1 scheduled — invocation-keyed FFT trace CLI

- session_id: 20261106T1511Z-T1-scheduled-invocation-cli-k7m2
- origin: scheduled
- issue: WATER-001 OPEN
- baseline_sha: 9b267bad42fe5e4be07b603d871564d86f5c214a
- scope_commit: ea8abee4ef919aa0420e4925cf1e7a73e9533dd5
- implementation: 60b7643aec7fb461c1538d2e6df840eb884a799f
- tests: bb02811fcbd22bf66de22db0d15151fe4fd5a46c; corrected padding d796b40a4e01f2ad05cb98881c453e53fade44aa
- experiment_key: water001-invocation-trace-cli-contract-k7m2
- taken_over_from: 20261106T1408Z-T1-scheduled-pair-input-readiness-v3
- status: source_added_unverified

## Owner evidence and live baseline
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner entered, saved, exited and reentered the world from run 42058825739 artifact; packaging publication failed. CL pin 520c4cf: water pass/kernel errors 23884/3850 in 220911 and 39132/6026 in 230108. No actual paired FFT readback proof, Unity FindKernel/Dispatch or device water fix is claimed. APK86 diagnosis is historical.

## New independent engineering
Existing scripts/t1_fft_trace_compare.py contains compare_invocations(), which detects invocation-keyed coordinate drift invisible to legacy histogram, but its CLI main() calls only compare(). Added scripts/t1_fft_invocation_trace_cli.py to expose strict invocation comparison, bounded binary reads, aggregate-only output and explicit exit codes 0=match, 1=mismatch, 2=invalid capture. Added five unit tests including reordered records, coordinate drift with equal values, duplicate invocation, bad sizes and legacy layout rejection. Kept existing shared comparator untouched. No Unity/Actions run duplicated.

## Verification limit
GitHub accepted commits above. Local runtime could not download GitHub sources because raw.githubusercontent.com DNS resolution failed; **tests are not yet executed**. No original/candidate same-input capture is present; no numerical parity claim.

## Next continuation
Run `python -m unittest tests.test_t1_fft_invocation_trace_cli -v` on actual checkout. Fix any failing tests; verify CLI with independently authenticated same-input/same-dispatch captures only after pair gate. Inspect latest HEAD and active T1 work before any GPU/Unity experiment. Do not change T4 mouse or T5 buttons/Resolution scope, preserve sound and Settings. Read this session and work JSON before continuation. NOT_READY 0/3.
