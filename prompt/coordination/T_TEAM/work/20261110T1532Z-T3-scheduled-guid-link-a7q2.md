# T3 scope 20261110T1532Z-T3-scheduled-guid-link-a7q2
origin=scheduled
issue_id=RENDER-002
status=active
base_observed_commit=9b89f62772c2c61f6269fd2249f8560af1522892 (recent search, branch lease not established)
resumed_from_session=20261110T1431Z-T3-scheduled-pair-ci-coverage-k8r2
intended_files=scripts/t3_unity_guid_link_audit.py; prompt/coordination/clients/T3/sessions/20261110T1532Z-T3-scheduled-guid-link-a7q2.md
experiment_key=t3-guid-link-static-audit-v1-source-only-no-private-assets
resource_key=none
hypothesis=Unity material shader/texture missing GUID targets or dummy GUID references can be separated from render-state mismatches by a read-only file-level static audit.
Constraints=No raw game data, no .meta mutations, no CI or Unity dispatch, no T4/T5 input edits. Scope independent of existing render-state pair tools. Recheck HEAD before any shared edit.
updated_at=2026-11-10T15:32:45Z
