# 20261110T2210Z-T1-scheduled-kernel6-negative-context-c3e8
origin=scheduled
role=T1
baseline_sha=9ac20bf03b827f175f8d48b15097a0e371fc6b5f
issue=WATER-001 OPEN NOT_READY
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; Artifact 42058825739 world/save/reentry succeeds; package publish fails. CL 220911-559: 23884 pass/3850 kernel; 230108-327: 39132 pass/6026 kernel.
experiment=T1-KERNEL6-NEGATIVE-CONTEXT-20261110
scope=scripts/t1_kernel6_log_context.py and new isolated tests/test_t1_kernel6_negative_context.py, independent from T4 mouse and T5 resolution/build.
hypothesis=Negative phrases such as 'kernel index 6 not found' and 'cannot find kernel index 6' are errors, but current same-line error matcher omits them; this causes false nonerror classification and --errors-only sample loss.
method=Add narrow negative-result phrases, regression test with synthetic lines, no raw CL or game assets. Verify local tests and avoid duplicate CI.
shared_resource=none
status=planned
