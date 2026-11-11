# T2 work — 20261111T0915Z-T2-scheduled-hardlink-input-h4n7
session_id=20261111T0915Z-T2-scheduled-hardlink-input-h4n7
origin=scheduled
issue_id=WATER-001
baseline_sha=bac9432d5dbfc3c9cb55d367b7b24a6f83b8f6a6
status=active
intended_files=scripts/t2_foam_publish_aggregate.py;tests/test_t2_foam_publish_aggregate.py;prompt/coordination/T_TEAM/clients/T2/sessions/20261111T0915Z-T2-scheduled-hardlink-input-h4n7.md
experiment_key=foam-aggregate-hardlink-source-output-same-inode-v1
resource_key=none
hypothesis=Distinct input/output pathnames may refer to the same inode via hard links, bypassing source==destination and overwriting source. Reject source/output same inode before publishing, add regression.
taken_over_from=20261111T0724Z-T2-scheduled-parent-symlink-q8r3
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md (phone world/save/reopen; water/FFT still failing)
constraints=No Unity, no game assets, no T3/T4/T5 files; no shader readiness claim.
next=Check tests and CI; then pursue Foam RenderTexture/CB0 lineage rather than expanding publisher hardening indefinitely.
