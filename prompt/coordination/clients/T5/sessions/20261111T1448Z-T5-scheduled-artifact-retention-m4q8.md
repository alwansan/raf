# T5 scheduled checkpoint 20261111T1448Z-T5-scheduled-artifact-retention-m4q8
origin: scheduled
base_sha: c8b178abd79d834356aa14d6a8d077516dbf0c34
resumed_from_sessions: 20261111T1348Z-T5-scheduled-ledger-identity-q7m2; 20261111T104622Z-T5-scheduled-ui-ci-7f2c
work: prompt/coordination/work/T5/20261111T1448Z-T5-scheduled-artifact-retention-m4q8.md (commit 513529f6395836282939ed272bc29741fa429530)

## Verified metadata audit
Owner report docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered world, saved and re-entered on artifact 42058825739; no full signed-byte match. GitHub API GET /repos/alwansan/raf/actions/runs/42058825739/artifacts yielded four diagnostic artifacts: 13431563116 (833 bytes), 13431483005 (1990), 13431363060 (3242), 13431142944 (2095). None named signed APK/OBB/XAPK. This is a run-scoped listing, not evidence that owner never downloaded a valid package: report separately names 13441227298 and 13441766832. Attempts to fetch those artifact IDs directly were rejected by connector URL allowlist, not a GitHub 404. The four archive SHA256 digests are archive digests, NOT signed APK or OBB checksums.

CI: latest run listing for branch showed T2 summary 43028966025 failed (prior checkpoint fixes event_id at d42a606); no evidence of rerun in that listing. Right-panel source CI 42998052750 success, not device validation. LogRaft owner 57 displayed samples avg 22.29 FPS, min 3.02, HUD 18.27 FPS/p95 82.82ms; not GPU times and not cross-build comparable.

No Unity, APK build, source edit, or mouse touch performed. No versionCode, signed APK manifest, OBB file bytes or device performance new proof. CL unchanged/read-only. No claim of readiness.

Next: find provenance of the two signed-output checkpoint IDs via associated delivery workflow, obtain immutable manifest and authorized signed binary for byte-level APK/OBB versionCode/name/size/SHA verification. Preserve Settings, T4 mouse ownership and NOT_READY 0/3.
