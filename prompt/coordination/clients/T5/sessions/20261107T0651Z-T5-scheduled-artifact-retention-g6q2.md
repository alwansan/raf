# T5 scheduled session 20261107T0651Z-T5-scheduled-artifact-retention-g6q2
origin: scheduled
scope_commit: 71cd4279e050c7b63df51901c3996be13b9aa3ce
baseline_sha: 13c36d0b57dc64f74b8b04469f56c99dae6a6049
resumed_from: 20261107T0552Z-T5-scheduled-retained-provenance-a8f3.md

## Verified 2026-11-07 06:51 UTC
Read owner feedback docs/DEVICE_FEEDBACK_42058825739_AR.md and current T_TEAM coordination. Owner device success applies only to run 42058825739, native SHA e9c358eda01785b65e4eb14f18723da426635628.
GitHub REST live /actions/runs/42058825739/artifacts: original signed checkpoint ID 13441766832 size 2974110506, expired=false, expires 2026-11-07T18:18:17Z; original delivery artifact absent.
Live /actions/runs/42110297871/artifacts: retained delivery ID 13454900880, 5948243834 bytes, expired=false, expires 2026-11-08T21:12:40Z; outer ZIP digest sha256:41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef.
Live /actions/runs/42296450023/artifacts: newer signed checkpoint ID 13550196498 size 2974171581 expires 2026-11-09T23:48:15Z; newer delivery ID 13549514149 size 5948365703 expires 2026-11-09T23:49:06Z. Newer native source a1737bd736e276d53df808442cfae3b1eea0d488 is not the phone-tested source.
Branch HEAD after scoped work 71cd4279e050c7b63df51901c3996be13b9aa3ce. No artifact downloaded, no permanent copy created; the retained artifact also expires and must not be described as durable. Outer ZIP digest is not proof of internal APK signer/versionCode or OBB size/SHA. No fresh LogRaft phone measurement, UI/Resolution/physical mouse code fix, Unity run, release or CI dispatch. T4 retains mouse ownership; T5 UI scope pending. NOT_READY 0/3.

## Actionable next
Before 2026-11-07T18:18:17Z UTC preserve original signed checkpoint in authorized durable storage, before 2026-11-08T21:12:40Z UTC preserve retained delivery. Verify manifest, APK signature/versionCode, main OBB filename/size/SHA, and correspondence to phone-installed version. Do not treat release 403 or retained outer digest as identity proof. Avoid duplicate native builds and other T agents' files.
