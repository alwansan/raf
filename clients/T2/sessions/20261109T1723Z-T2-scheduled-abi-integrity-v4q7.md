# T2 scheduled checkpoint — Foam report source metadata integrity
session_id: 20261109T1723Z-T2-scheduled-abi-integrity-v4q7
origin: scheduled
baseline_sha: ae69a9380f730ff7d595389533fdf055ada8ea6f
scope_commit: 2d22853751f99c679e9b853f9b0cbc77a3540fa3
source_commit: 60b81a61228bcf4d1f3dfd4159e1b958896af3ca
test_commit: ce62532c4dc81e4b0a544bbd251361999f6ea3f5
observed_head: ce62532c4dc81e4b0a544bbd251361999f6ea3f5
work: work/experiments/20261109T1723Z-T2-scheduled-abi-integrity-v4q7.md
origin_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, artifact 42058825739; world enter/save/re-entry confirmed; water/FFT errors unresolved.

Result: Revalidated original_numeric_table_rows keys, exact int values, original_descriptor_rows exact int and sum, and 64-character lowercase hex source descriptor digest in the final Foam resource report verifier. This closes a trust gap when an already-combined JSON report is mutated before verification. Added regression tests for forged source counts, bool/float, extra fields and malformed hashes. No private names or original shader bytes published.

Verification: GitHub commits accepted. Git local access unavailable due to DNS (github.com resolution failure); no local Python test execution. Prior CI 42653175246 success at c24317d8 predates this change and does NOT prove these new tests. No new CI dispatched; inspect subsequent path-filtered workflow run and run tests if not automatically triggered.

Scope: WATER-001 OPEN / NOT_READY. This is integrity checking, not original texture-object identity or ShaderLab/Unity/device pixel proof. T3 effects, T4 mouse, T5 Resolution and shared mini APK untouched. Next: execute python -m unittest tests.test_t2_foam_resource_abi on current HEAD in source-only CI; continue Mono.Cecil Foam pass1 receiver/texture identity, source CB0, Spectrum/Blur bindings and ShaderLab only after original evidence.\n