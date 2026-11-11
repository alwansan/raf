# T3 scope 20261111T2238Z-T3-scheduled-fileid-k7m4
origin=scheduled
issue_id=RENDER-002
status=source_change_pending_ci
baseline_sha=4ee7f5a6dfec0a7e88ceedd0f3e6c873aeb57664
intended_files=scripts/t3_material_dependency_pair_audit.py; tests/test_t3_material_dependency_pair_audit.py
experiment_key=t3-paired-material-texture-fileid-subasset-negative-control-v1
resource_key=none
hypothesis=GUID-only texture pointer comparison misses changed fileID/type under same GUID.
implemented_commits=5ca91a8ec973641c32260f8f3bd1a4418c3da818;9930a38dd09147c80561676f7d670b3c7e6e4dda
verification=static only; no tests run; no source/export original or device evidence
session=prompt/coordination/clients/T3/sessions/20261111T2238Z-T3-scheduled-fileid-k7m4.md
next=execute synthetic tests; authenticated original/export pointer pair
