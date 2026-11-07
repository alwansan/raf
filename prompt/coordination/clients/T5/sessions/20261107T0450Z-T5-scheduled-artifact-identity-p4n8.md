# T5 scheduled session 20261107T0450Z-T5-scheduled-artifact-identity-p4n8
origin: scheduled
base_sha: 1aa27098cf40bc0bc6863ad293e6c9bcf7a8fbee
scope_commit: 7887a52560145b9acfc0b0b41dd6996afccab852
work: prompt/coordination/clients/T5/work/20261107T0450Z-T5-scheduled-artifact-identity-p4n8.md
resumed_from_session: 20261107T0350Z-T5-scheduled-artifact-expiry-c8e4.md

## New verified cross-run provenance finding (2026-11-07 04:50 UTC)
GET /actions/runs/42058825739: source e9c358eda01785b65e4eb14f18723da426635628, completed/failure. GET /actions/runs/42296450023: source a1737bd736e276d53df808442cfae3b1eea0d488, completed/failure. These are different immutable candidates. Owner's successful phone world/save/reopen belongs only to 42058825739.

GET /actions/runs/42058825739/artifacts: signed checkpoint **13441766832** size **2974110506**, expired=false, expires **2026-11-07T18:18:17Z**. The owner's report also identifies delivery artifact **13441227298**, but this artifact is **not present in the current API artifact listing**; do not assume it can still be downloaded. GET /actions/runs/42296450023/artifacts: signed checkpoint **13550196498**, size **2974171581**, expires **2026-11-09T23:48:15Z**, and delivery **13549514149**, size **5948365703**, expires **2026-11-09T23:49:06Z**; both expired=false at inspection. Source/size/IDs differ; do not substitute the newer untested build for the owner-tested APK or infer APK/OBB SHA equality.

## Boundaries
Read-only metadata audit, no download, no hash or package installation, no LogRaft new measurements, no Unity/Release mutation. Owner report's 22.29 estimated FPS and HUD 18.27 FPS are older session-specific figures, not GPU time. T4 physical mouse is separate. T5 right buttons/Resolution still pending. No READY claim.

## Next actions
**Urgent:** authorized actor should preserve owner-tested signed checkpoint 13441766832 **before 2026-11-07 18:18:17 UTC**, then newer run 42296450023 checkpoint/delivery before 9 Nov UTC. Inspect manifest, APK versionCode and signer, OBB name/size/SHA and delivery.json from downloaded bytes. Confirm why old delivery 13441227298 is absent, without guessing deletion cause. Compare package identity before using LogRaft CL samples. Investigate release HTTP403 without re-running Unity. No duplicated CI; full readiness NOT_READY 0/3.
