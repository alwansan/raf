# T5 artifact delivery retrieval audit
session_id: 20261111T1550Z-T5-scheduled-artifact-404-p9v3
origin: scheduled
issue_id: DELIVERY-42058825739
base_sha: d9896fbbbcdcb8b0372005a15ff06dc97b7cce07
intended_files: prompt/coordination/work/T5/20261111T1550Z-T5-scheduled-artifact-404-p9v3.md; prompt/coordination/clients/T5/sessions/20261111T1550Z-T5-scheduled-artifact-404-p9v3.md
experiment_key: artifact-id-13441227298-13441766832-download-api-20261111
resource_key: none (read-only API)
status: completed
hypothesis: run-scoped artifacts do not prove signed-output checkpoints inaccessible.
result: Direct authenticated GitHub download_workflow_artifact for IDs 13441227298 and 13441766832 returned HTTP 404 Not Found for BOTH on 2026-11-11 ~15:50 UTC. Earlier generic fetch 400 was an endpoint allowlist rejection and was inconclusive; this new direct action is decisive for current accessibility through connected GitHub credentials, but cannot distinguish expiration, deletion, changed permissions, or mistaken IDs. No signed APK/OBB bytes, manifest, or SHA256 verified. Owner phone save/load success remains valid only for tested install.
next: locate immutable release/copy or rebuild from pinned e9c358eda01785b65e4eb14f18723da426635628 under team build coordination, then compare APK versionCode and OBB name/size/SHA256. Do not fabricate hashes.
