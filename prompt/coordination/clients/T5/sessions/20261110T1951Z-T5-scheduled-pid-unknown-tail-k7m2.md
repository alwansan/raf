# T5 session 20261110T1951Z-T5-scheduled-pid-unknown-tail-k7m2
origin=scheduled; date_utc=2026-11-10T19:51Z
branch=feature/android-native-port; baseline_sha=02a942edb9d940fe468e703597136f86be71f971

## Read and evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM/CHAT_AND_SCHEDULE_AR.md, PROMPT_AR.md, OPERATING_MODEL_AR.md, T5 state/MEMORY, source and tests. Device owner 42058825739 passed world entry/save/re-entry; signed APK/OBB identity, right-side three buttons, Resolution and current device FPS remain unverified.
CI 42868458735 source-pinned-cl-metrics failed three startup-prefix tests (18+6+8 other tests passed). Current source scripts/t5_cl_pid_epoch_audit.py includes startup-prefix handling from f5a29e49c521b2eb46af486d951b131a8011afd4. Do not mistake old CI failure for a new failure of that fix.

## Work done
Plan: prompt/coordination/work/T5-20261110T1951Z-T5-scheduled-pid-unknown-tail-k7m2.md commit 399e01f4e3ba1df1f24bfb5e2074f3e0c72ba9fb. Added one source-only regression to tests/test_t5_cl_pid_startup_prefix_real_gate.py commit 67a1b0f142aa64a9b7c130685b6f401a3b4d7e51: an unknown process state AFTER a verified PID must split cohorts even if the PID is reused. Expected epochs=3, no cross-epoch FPS median. Existing workflow path trigger should run CI; result not verified at session close. No Unity build, no real CL download, no phone test, no other agent file changes.

## Follow-up
Check new GitHub Actions run for commit 67a1b0f (workflow raft-t5-cl-real-fps-cohort.yml), inspect job steps and pinned CL result. If fail, fix only demonstrated regression. Then return to owner P0: actual three-button right safe area + existing Resolution, APK/OBB signed manifest verification, same-scene LogRaft metrics. Coordinate with T4 for physical mouse, avoid duplicate Unity or Mini builds. Preserve NOT_READY 0/3.
