# T2 scoped work 20261111T0325Z-T2-scheduled-input-boundary-n6q4
origin=scheduled
base_sha=c200ec56a5e369d9fe4e9f740bb34e185779db20
issue=WATER-001 OPEN / NOT_READY 0/3
files=scripts/t2_foam_publish_aggregate.py; tests/test_t2_foam_publish_aggregate.py; independent T2 session/work files
hypothesis=The opt-in publisher can read a symlink to an unintended private input or block on non-regular inputs; reject before opening.
experiment_key=T2-FOAM-PUBLISH-INPUT-TYPE-20261111
shared_resource=none; no Unity/CI dispatch; workflow path filter runs automatically.
Owner evidence: DEVICE_FEEDBACK_42058825739_AR.md, world/save/re-entry succeeds but water/FFT remains broken.
Prior proof: CI 42946063315 SUCCESS on 5dd7459 (publisher tests); new source changes require new CI verification.
