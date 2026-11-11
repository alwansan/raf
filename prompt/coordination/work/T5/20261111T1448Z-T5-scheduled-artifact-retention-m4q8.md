# T5 DELIVERY-001 scope 20261111T1448Z-T5-scheduled-artifact-retention-m4q8
origin: scheduled
base_sha: c8b178abd79d834356aa14d6a8d077516dbf0c34
issue_id: DELIVERY-001 / APK-OBB provenance
status: completed (read-only metadata audit)
intended_files: this work record and prompt/coordination/clients/T5/sessions/20261111T1448Z-T5-scheduled-artifact-retention-m4q8.md
experiment_key: T5-ARTIFACT-LIST-42058825739-20261111
resource_key: none (GitHub metadata only)
hypothesis: the owner report's signed output artifacts can be independently located by the run artifacts API and compared to signed APK/OBB manifests.
result: GitHub REST GET /repos/alwansan/raf/actions/runs/42058825739/artifacts returned only four tiny diagnostic artifacts (833,1990,3242,2095 bytes); no signed APK/OBB/XAPK entry in this response. Report cites signed output checkpoints 13441227298 and 13441766832; those IDs must be checked individually or under their actual runs. Run 42058825739 itself is not proof of currently downloadable signed bytes.
limits: no binary downloaded, no versionCode, OBB file SHA or signature matched. No phone FPS or GPU inference. Do not equate artifact archive digest with embedded APK/OBB digest. T4 mouse and Unity untouched.
next: inspect artifact IDs 13441227298 and 13441766832 via API, find associated run and manifest, obtain authorized signed bytes and compare exact SHA/versionCode/OBB name before attribution.
