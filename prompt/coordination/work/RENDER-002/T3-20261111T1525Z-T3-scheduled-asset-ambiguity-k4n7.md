# T3 independent scope
session_id=20261111T1525Z-T3-scheduled-asset-ambiguity-k4n7
origin=scheduled
issue_id=RENDER-002
base_sha=ea389f6612fe23bfa5c795b7d18781db34304ee4
status=active
updated_at=2026-11-11T15:25:39Z
intended_files=scripts/t3_material_texture_binding_audit.py;tests/test_t3_material_texture_binding_audit.py;prompt/coordination/clients/T3/sessions/20261111T1525Z-T3-scheduled-asset-ambiguity-k4n7.md
experiment_key=T3-TEXTURE-ASSET-AMBIGUITY-CLASSIFICATION-v1
resource_key=none (synthetic Python source-only)
hypothesis=.asset is an ambiguous Unity serialized asset extension; reporting it as a verified texture meta creates false positives. Classify separately without leaking paths or GUIDs.
No Unity/ZIP2/CI dispatch or game resource mutation. Check latest branch and overlaps before modifying source. Preserve T4/T5 scope.
