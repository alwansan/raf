# T3 scope — orphan texture meta false-positive
session_id=20261111T1626Z-T3-scheduled-orphan-texture-meta-n6p4
origin=scheduled
issue_id=RENDER-002
base_sha=40e7b1670df015c627f1a85d3a67925f6487bf54
status=active
intended_files=scripts/t3_material_texture_binding_audit.py;tests/test_t3_material_texture_binding_audit.py;prompt/coordination/clients/T3/sessions/20261111T1626Z-T3-scheduled-orphan-texture-meta-n6p4.md
experiment_key=T3-TEXTURE-ORPHAN-META-OWNER-20261111-v1
resource_key=none (source-only, no Unity or APK)
hypothesis=The existing unique texture GUID category incorrectly counts an orphan image.png.meta with missing image.png as proof of a texture asset. Require actual owner file before classifying.
taken_over_from=20261111T1525Z-T3-scheduled-asset-ambiguity-k4n7
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; CI41939404454 25 external references unresolved
constraints=No game raw assets; preserve GUID and scenes; no overlapping Unity/CI; no claim of device fix.
