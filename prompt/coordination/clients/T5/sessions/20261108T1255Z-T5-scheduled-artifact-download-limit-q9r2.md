# T5 session 20261108T1255Z-T5-scheduled-artifact-download-limit-q9r2
origin: scheduled
resumed_from_session: 20261108T1050Z-T5-scheduled-artifact-digest-k8q4; 20261108T0950Z-T5-scheduled-t4-ci-recovery-c71e (chat-reported)
base_sha: d9b9267d405868b2a528cd875661df7a2b3a439f
scope_commit: bb474b42ea910ef0c54ebfc3510d5ce7c75a4b30
issue: DELIVERY-ARTIFACT-42058825739
work: prompt/coordination/clients/T5/work/20261108T1255Z-T5-scheduled-artifact-download-limit-q9r2.md
## Evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md before prioritizing. Owner confirms world entry/save/exit/reopen only on run42058825739 source e9c358eda01785b65e4eb14f18723da426635628. No signed installed APK/OBB hashes known. Read AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM/PROMPT_AR.md, OPERATING_MODEL_AR.md, CHAT_AND_SCHEDULE_AR.md, TRIAL_BUILD_READINESS.md; inspected latest T5 session and T5 state, branch HEAD and Actions.
At 2026-11-08 ~12:55 UTC, run42110297871 artifact13454900880 retained (expired=false), 5948243834 bytes, expires_at 2026-11-08T21:12:40Z, outer archive sha256 41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef.
New decisive connector experiment: attempted download_workflow_artifact(13454900880) to secure bytes; returned `InvalidInputException: Artifact exceeds max size of 536870912 bytes: 5948243834 bytes`. No archive was copied or downloaded. This connector's 512MiB limit is below the 5.95GB archive; do not repeat unchanged attempt. An authorized GitHub runner or local gh CLI with >6GB storage and a private destination is required to retain it. Avoid public game asset uploads.
No Unity run launched, no T4 files changed. CI42472339258 source-only mouse classifier success, not phone evidence. Trial votes not 5/5, no new build. Three right-side buttons reportedly moved in prior commits acc964d0 and 96f41443, device acceptance absent. Android Resolution guard does not establish render scale selection. LogRaft FPS is SurfaceFlinger display estimate, not Unity GPU time.
## Result and next
Blocked specifically on artifact connector's hard 512MiB download limit. Need private destination and runner/gh client before expiry; then outer digest verification, signed APK/OBB hashes/versionCode/OBB name and device-side comparison. Independently address Resolution actual render scale with existing Settings and preserve landscape/aspect; test three buttons on device. Full readiness NOT_READY; no fabricated device test.
