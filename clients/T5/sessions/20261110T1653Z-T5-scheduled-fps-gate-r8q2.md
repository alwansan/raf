# T5 session 20261110T1653Z-T5-scheduled-fps-gate-r8q2
origin: scheduled
resumed_from_sessions: 20261110T1554Z-T5-scheduled-fpsjson-k7m2.md; 20261110T1153Z-T5-scheduled-c7e4.md
base_sha: be6da8041a61788d55624294959413c87f61f02c
work_commit: 2db12cb8d38fadbe6dba55c5d4b24572456fc37c
issue: PERF-007

## Verified result
Read owner report docs/DEVICE_FEEDBACK_42058825739_AR.md and AGENTS.md, CURRENT_OWNER_REQUIREMENTS.md, STATUS.md and live T_TEAM protocol. Run https://github.com/alwansan/raf/actions/runs/42849324096 at 2026-11-10T15:54:49Z was **skipped**, not successful; job https://github.com/alwansan/raf/actions/runs/42849324096/job/129945307505 was skipped with zero steps. This is explained exactly by .github/workflows/raft-t5-cl-real-fps-cohort.yml job guard: push needs [t5-cl-real-fps-cohort] in head commit message; commit 116fc83b has no marker. Thus JSON duplicate-key fix 116fc83b and tests c47854e remain without demonstrated execution from that run. Existing successful run 42819012779 validates a different APK/OBB pair check, not PERF-007. No new CI dispatched, no Unity or phone run claimed.

Owner-confirmed game world save/reopen only for artifact 42058825739; CL source pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Previous FPS samples 57 fresh in 220911 and 2 fresh in 230108; not a comparable performance cohort. No signed APK/OBB internal pairing or resolution/right-buttons fix in this session.

## Next
Execute PERF-007 tests on a genuinely eligible workflow_dispatch or substantive code commit with guard marker, only after checking ongoing runs. Review latest T4 ownership before UI changes; maintain separate Resolution/right-side button scope. Match signed delivery.json/APK/OBB, then compare CL PID epochs and render-error onset. No full game build without trial readiness policy.

status: completed_diagnostic; source_validation_pending
