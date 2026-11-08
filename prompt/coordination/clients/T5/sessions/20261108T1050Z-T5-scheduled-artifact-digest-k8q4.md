# T5 session 20261108T1050Z-T5-scheduled-artifact-digest-k8q4
origin: scheduled
base_sha: 43c03afdab3de74c21129dc272cbdd16ce62e16e
scope_commit: a4a6656d2f43e83ed3e408f4523ce47acdcc5cc5
head_before_session: a4a6656d2f43e83ed3e408f4523ce47acdcc5cc5
resumed_from_session: 20261108T0950Z-T5-scheduled-t4-ci-recovery-c71e (prior checkpoint reported in chat); 20261108T0850Z-T5-scheduled-artifact-expiry-b6f2

## Pinned evidence and result
Owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md: world entry/save/exit/reopen only on run42058825739, source e9c358eda01785b65e4eb14f18723da426635628. The report distinguishes delivery artifact13441227298 and signed checkpoint13441766832; delivery publishing failed.
Live GitHub REST GET /repos/alwansan/raf/actions/runs/42110297871/artifacts at 2026-11-08 ~10:50 UTC returned exactly one retained archive: id13454900880, name t5-retained-native-delivery-42058825739, size 5948243834 bytes, expired=false, expires_at 2026-11-08T21:12:40Z, GitHub archive digest sha256:41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef, originating rescue run head df6144411a130cc1ac23f1df4ae7f653d61e9704. This digest describes the archive, NOT the APK/OBB inside it and NOT the installed phone binaries. No bytes downloaded or published. No durable retention beyond expiry established.
Fresh branch HEAD before work 43c03afdab3de74c21129dc272cbdd16ce62e16e (T4 classifier checkpoint). GitHub Actions run42472339258 completed success on e1e7ac93cdb64af5efdf8a819b74157dfcb71497, source-only T4 classifier; not device acceptance.

## Constraints and next action
No Unity or native run requested; no T4 files touched; no gameplay source altered. Artifact provenance is still incomplete: acquire signed APK/OBB via authorized private destination and compute per-file SHA256, package/versionCode/OBB naming, then compare actual installed binaries. Before any new code edits inspect live UI and Resolution work scopes: prior docs/T5_RESOLUTION_ANDROID_POLICY_REVIEW_2026-11-05.md confirms right-hand buttons already moved in acc964d0 and 96f41443, not yet phone-tested; existing Android resolution guard is NOT lower render resolution support. T4 owns physical mouse. LogRaft SurfaceFlinger estimates must not be called Unity FPS. Full readiness NOT_READY 0/3.
