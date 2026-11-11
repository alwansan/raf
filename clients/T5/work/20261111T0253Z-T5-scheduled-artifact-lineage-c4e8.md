# T5 independent scope — delivery lineage verification
session_id: 20261111T0253Z-T5-scheduled-c4e8
origin: scheduled
issue_id: DELIVERY-ARTIFACT-PROVENANCE
status: active
base_sha: d22add56f3987fe018b978dada01d6735e12f75f
intended_files: clients/T5/work/20261111T0253Z-T5-scheduled-artifact-lineage-c4e8.md; clients/T5/sessions/20261111T0253Z-T5-scheduled-c4e8.md
experiment_key: artifact-list-vs-signed-checkpoint/42058825739/42222494746/20261111
resource_key: none; GitHub API metadata read-only
updated_at: 2026-11-11T02:53:45Z
hypothesis: delivery artifact IDs 13441227298 and 13441766832 in owner feedback can be fetched as current run 42058825739 artifacts. API returns only four tiny diagnostics (833,1990,3242,2095 bytes); neither delivery ID present. Prior independent run 42222494746 success does not itself establish full SHA256 or APK signature. Do not conflate run's current artifact listing with historical owner download, and do not infer files missing from phone.
Acceptance: independently read signed APK manifest, APK signing certificate digest, full APK/OBB SHA256, OBB basename/main.versionCode.package, bytes, embedded manifest and on-device install provenance; compare exact source e9c358e and owner-tested package. No files or phone access in this run. Existing metadata versionCode89 APK672853870 OBB2301256312 from previous independent report are metadata-only, not full-byte verification.
Avoid overlap: T4 owns mouse; T5 owns packaging provenance; no Unity build or release dispatched.
