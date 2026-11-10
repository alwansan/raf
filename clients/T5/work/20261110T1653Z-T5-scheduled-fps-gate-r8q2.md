# T5 work 20261110T1653Z-T5-scheduled-fps-gate-r8q2
session_id: 20261110T1653Z-T5-scheduled-fps-gate-r8q2
origin: scheduled
issue_id: PERF-007
status: completed (CI eligibility diagnosis; runtime validation still open)
base_sha: be6da8041a61788d55624294959413c87f61f02c
intended_files: clients/T5/work/20261110T1653Z-T5-scheduled-fps-gate-r8q2.md; clients/T5/sessions/20261110T1653Z-T5-scheduled-fps-gate-r8q2.md
experiment_key: cl-fps-json-duplicate-keys/116fc83b/520c4cf/eligibility-gate
resource_key: none (read-only GitHub Actions inspection)
updated_at: 2026-11-10T16:53:00Z

Hypothesis: run 42849324096 validates the newly added duplicate-JSON-key rejection. Rejected: the workflow job was skipped, so there is no test execution. The job-level if requires workflow_dispatch or push commit message containing [t5-cl-real-fps-cohort]; actual push message was 'T5: reject duplicate JSON keys in LogRaft FPS cohort input'. Both run and sole job are skipped, with no steps and no runner. Do not report CI PASS from this run. No duplicate Unity or CL run launched. Next: execute the already existing four test suites on an eligible distinct source revision or explicit workflow_dispatch after checking running workflows; avoid trigger-only commits.