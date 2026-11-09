# T5 isolated scope — strict evidence tokens
session_id: 20261109T0153Z-T5-scheduled-evidence-token-p6m2
origin: scheduled
baseline_head: e330628195fdc2720426735f7a929d2074acfb40
issue: shared-mini evidence integrity / T3 screenshot verification
experiment_key: t5-evidence-token-boundary-20261109
resource_key: none; no Unity or CI launched
files: scripts/t5_verify_shared_device_summary.py; scripts/test_t5_verify_shared_device_summary.py; this work note; independent T5 session
hypothesis: substring checks can accept forged marker fragments (e.g. unverified_surface_pixels=true or not_gl_error=0x0) and incorrectly label a capture as evidence-ready.
coordination: no changes to T4 mouse, Raft game UI, OBB or Unity; isolated source tests. Baseline prior T5 commit 069abc5. No claims of phone acceptance.
status: scoped; expected file blob SHA required on update; no force.
