# T5 scope 20261109T1356Z-T5-scheduled-artifact-run-scope-n4q8
origin=scheduled
baseline_sha=3f5dfcd5e7a445dd6eb424c79e8f865ea0d650ff
experiment_key=T5-42058825739-RUN-ARTIFACT-ENUM-20261109
files=this work file and clients/T5/sessions/20261109T1356Z-T5-scheduled-artifact-run-scope-n4q8.md
shared_resource=none; read-only GitHub API; no Unity build, no T4 files.

## Verified experiment
GET /repos/alwansan/raf/actions/runs/42058825739/artifacts?per_page=100 on 2026-11-09 UTC returned four run-scoped artifacts: 13431563116 (833 B), 13431483005 (1990 B), 13431363060 (3242 B), 13431142944 (2095 B). All report expiry 2026-11-12 and are tiny diagnostic/staging outputs. Neither 13441227298 nor 13441766832 from owner feedback is present in this run-scoped listing. This does NOT prove those two artifacts do not exist: they may belong to downstream delivery/checkpoint runs. Never treat tiny staging outputs as installed APK/OBB, nor infer package hashes from artifact ZIP digest.

## Decision
PACKAGE_UNMATCHED remains. Resolve the downstream run IDs for artifact 13441227298 and signed checkpoint 13441766832 from workflow provenance, then extract signed APK manifest versionCode and OBB member name/size/SHA from the same checkpoint. Do not re-download 6GB blindly. Phone success remains only for owner-tested package; no performance comparison or GPU timing is proven. Right-side buttons source-fixed / phone-pending, Resolution render-scale unimplemented; T4 physical mouse excluded.
status=PROVENANCE_RUN_SCOPE_CONFIRMED; PACKAGE_UNMATCHED; NOT_READY.
