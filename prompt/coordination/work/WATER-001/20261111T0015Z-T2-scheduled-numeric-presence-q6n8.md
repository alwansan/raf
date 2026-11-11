# T2 scoped work 20261111T0015Z-T2-scheduled-numeric-presence-q6n8
origin: scheduled
issue_id: WATER-001
base_sha: f241710f070baba0a40a8e58177a34f5e1e70f9e
status: waiting_ci
experiment_key: t2-foam-producer-private-numeric-pair-presence-consistency-v1
resource_key: none (source-only Python)
intended_files: scripts/t2_foam_texture_identity.py; tests/test_t2_foam_json_product_guard.py; prompt/coordination/clients/T2/sessions/20261111T0015Z-T2-scheduled-numeric-presence-q6n8.md; this work file
hypothesis: compare_private_names currently counts forged numeric pairs even if descriptor field_presence says absent; fail closed on inconsistent presence and out-of-domain values, including -1 sampler sentinel.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; run 42058825739 world save/reopen succeeded, water still fails; do not overwrite device evidence.
coordination: no T3 fire/smoke, T4 mouse, T5 Resolution, Unity or shared lab modifications. Prior T2 CI producer schema gate exists; no duplicate dispatch.
next: implement and locally exercise synthetic cases; check CI after commit.

result_commit: ea6b818b30bb027eda93c0b78e768a354da86b41
result: fail-closed numeric-pair consistency check added to actual Foam producer and three synthetic regression methods. Existing CI workflow watches both changed paths. New CI result not yet observed.
limits: no original Foam, Unity or Android execution; no claim of texture binding or device water.
next: inspect CI for ea6b818, verify tests, then inspect authentic pass0-to-pass1 RenderTexture instance/CB0 identity.
