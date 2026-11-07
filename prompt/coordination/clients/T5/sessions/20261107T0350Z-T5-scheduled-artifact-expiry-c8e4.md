# T5 scheduled session 20261107T0350Z-T5-scheduled-artifact-expiry-c8e4
origin: scheduled
baseline_sha: 6c19f46efd9d9ca91747960171c89166093ba225
work: prompt/coordination/clients/T5/work/20261107T0350Z-T5-scheduled-artifact-expiry-c8e4.md
resumed_from: 20261107T0246Z-T5-scheduled-release-permission-matrix-6a91.md

## Verified finding
Read docs/DEVICE_FEEDBACK_42058825739_AR.md and T_TEAM live instructions. GitHub Actions run 42296450023 has reconstruct success and release publication failure HTTP403 (previous log evidence). Fresh artifacts API confirms raft-android-signed-output-checkpoint id 13550196498 size 2974171581 expires 2026-11-09T23:48:15Z; raft-android-test-delivery id 13549514149 size 5948365703 expires 2026-11-09T23:49:06Z. Both unexpired at observation. The workflow already has GH_TOKEN secrets.RAFT_RELEASE_TOKEN || github.token and job contents:write; do not claim that adding contents:write fixes this. No release retry or native build triggered.

## Boundaries and continuation
No file bytes downloaded, no signing/OBB pairing or phone performance claim. Owner's device world/save/reentry evidence is limited to artifact 42058825739. T4 owns physical mouse; T5 right-side buttons and Resolution remain open. Next: urgently preserve run 42296450023 artifacts before expiry with authorized release/download route; compare signed APK and OBB with manifest, then diagnose release 403 using effective token and tag policy, avoiding token disclosure. No CI/device claim. NOT_READY 0/3.
