# T2 scheduled — original Foam report schema audit

- session_id: 20261108T0016Z-T2-scheduled-original-schema-gap-k6p2
- origin: scheduled
- source: feature/android-native-port; prior checkpoint: 618fdff09190d22cf41245c93b24fa00ac029336
- owner phone baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; source e9c358eda01785b65e4eb14f18723da426635628; world enter/save/re-enter succeeded on owner's device; water/FFT still failed.
- latest original pass role evidence: run 42308583977, pass0 RenderTexture→RenderTexture, pass1 source/destination unknown. This is static IL evidence only.
- scope: prompt/coordination/work/WATER-001/20261108T0016Z-T2-scheduled-original-schema-gap-k6p2.json; no overlap with T3 shader/material files, T4 mouse/Resolution or T1 FFT.

## New source audit finding

Read current scripts/t2_foam_pass_crosscheck.py, scripts/t2_foam_pass_role_gate.py, tests/test_t2_foam_pass_crosscheck.py and original report validator scripts/t2_foam_shaderfind_return_report.py. The existing 81-combination crosscheck test patches validate_original and therefore proves role/count reconciliation **only**, not acceptance of a genuine full original schema. Another test proves the validator is called but deliberately makes it throw; there is no end-to-end positive test with a complete authenticated original-safe report in this test module. This is a test-coverage limitation, **not** evidence that the real validator is broken. Do not label the 81 tests as end-to-end.

## Execution and limitations

- Checked branch delta since 618fdff: 11 commits, no overlapping T2 code edits in changed-file list. Existing original-data run 42308583977 is sufficient; no redundant CI or Unity request.
- Git clone from this runner failed DNS resolution of github.com; GitHub connector read succeeded. Did not fabricate source artifact, original IL, or device success. No game shader/CB0/ShaderLab changes and no change to audio/Settings, .meta/GUID or deferred touch.
- Next concrete test: construct an authenticated **safe** fixture matching the complete t2_foam_shaderfind_return_report schema, execute reconcile() with validate_original **unmocked** and a matching two-site report; separately mutate one original count and one authentication flag and assert fail-closed. Prefer a sanitized genuine report artifact if available; do not publish original names or raw IL.
- WATER-001 OPEN. Trial-build vote remains no from T2: no integrated GPU shader change yet.
