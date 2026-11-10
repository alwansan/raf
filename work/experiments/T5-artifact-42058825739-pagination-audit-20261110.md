# T5 artifact provenance audit — 2026-11-10 UTC
session_id: 20261110T0655Z-T5-scheduled-a91c
origin: scheduled
baseline_sha: 916f689f9fa368218c551e7abcb628bd5d1033a4
experiment_key: T5-ARTIFACT-PAGINATION-42058825739-01
scope: GitHub Actions artifact inventory and signed APK/OBB provenance; no game source or T4 files.
shared_resource: none; read-only API queries.
hypothesis: delivery artifacts 13441227298 and 13441766832 were missing from a truncated first page of run artifacts.
method: GET /repos/alwansan/raf/actions/runs/42058825739/artifacts?per_page=100&page=1 and page=2; run metadata.
result: **hypothesis rejected**. GitHub API reports total_count=4, exactly four diagnostics IDs 13431563116, 13431483005, 13431363060, 13431142944; page 2 empty. Run completed failure. IDs 13441227298 and 13441766832 cited by docs/DEVICE_FEEDBACK_42058825739_AR.md are NOT returned as artifacts belonging to run 42058825739 at audit time. This does not prove deletion: IDs may belong to a separate workflow run, may be inaccessible, or report may refer to different endpoints. Do not claim signed package SHA or installable provenance without manifest/bytes.
next: locate IDs by workflow/job context, obtain manifest and APK/OBB SHA256 and versionCode from actual downloaded package; verify LogRaft session association. Keep device acceptance limited to owner-reported 42058825739.
links: https://github.com/alwansan/raf/actions/runs/42058825739 ; https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md
