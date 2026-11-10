# T2 scheduled — repair syntactically invalid Foam RHS Python
session_id: 20261110T0425Z-T2-scheduled-literal-newline-fix-q7m2
origin: scheduled
baseline_sha: 77138848e62a4b297f945106305f6e43209d0212
scope_commit: 4d898ca4c1676cca782fa7130b2db7643622d092
source_commit: 4e68bfb7e3af51307aadf057fd6407d02a70e822
test_commit: bee055f052781f1389a6a171fa9a0971c5c30f3a
work: work/experiments/20261110T0425Z-T2-scheduled-literal-newline-fix-q7m2.md
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, original phone world enter/save/reentry; WATER-001 unresolved.
resumed_from: clients/T2/sessions/20261110T0220Z-T2-scheduled-rhs-stack-order-n6q4.md
finding: Both script and unittest source contained literal backslash-n sequences in Python statement context (five in script, six in test). This produces invalid Python syntax and blocks tests before any assertion. Replaced with real line separators, without modifying classification semantics.
verification: connector fetched original UTF-8 file and committed the two surgical edits with GitHub blob-SHA conditional writes. Local Python execution NOT VERIFIED: container cannot resolve github.com; no CI duplicate launched. Re-read and execute python -m unittest -v tests.test_t2_foam_rhs_classifier_synthetic on immutable commit before claiming PASS.
limits: synthetic CIL, not original Foam IL, ShaderLab integration, or runtime RenderTexture identity. WATER-001 OPEN / NOT_READY 0/3.
next: run syntax/13-case regression on immutable SHA, inspect any additional escaped-newline syntax defects, then integrate actual Mono.Cecil RHS receiver tracing and source-proven texture bindings.
