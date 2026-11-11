# T1 scope — 20261111T0706Z-T1-scheduled-count-partition-5c81
origin=scheduled
baseline_sha=8d05dfc6d1132651148f94777f9b0bc70cc0e8a5
issue=WATER-001
experiment=T1-KERNEL6-COUNT-PARTITION-20261111
files=scripts/t1_compare_kernel6_sessions.py; scripts/test_t1_kernel6_count_partition.py; work/T1-20261111T0706Z-T1-scheduled-count-partition-5c81.md; clients/T1/sessions/20261111T0706Z-T1-scheduled-count-partition-5c81.md
shared_resource=none; Unity/CI/build=none
hypothesis=Sanitized comparison accepts kernel6 mention totals inconsistent with error and non-error partitions; an inconsistent export must fail closed before any cross-session delta.
evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; pinned CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57; earlier T1 cross-session triage.
scope_exclusion=T4 mouse/pointer capture, T5 resolution/three buttons, T2 water materials; preserve all.
result=source contract and four synthetic regression cases staged; no CL or device proof.
