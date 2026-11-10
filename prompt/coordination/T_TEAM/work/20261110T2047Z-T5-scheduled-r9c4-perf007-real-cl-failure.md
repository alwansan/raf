# T5 work scope
session_id: 20261110T2047Z-T5-scheduled-r9c4
origin: scheduled
issue_id: PERF-007
status: active
base_sha: 7c3e38188c09943e9c485e2e0974130e3b3c15ee
intended_files: prompt/coordination/T_TEAM/work/20261110T2047Z-T5-scheduled-r9c4-perf007-real-cl-failure.md; prompt/coordination/T_TEAM/clients/T5/sessions/20261110T2047Z-T5-scheduled-r9c4.md
experiment_key: PERF007-real-CL-520c4cf-run42889557850
resource_key: none
hypothesis: real pinned CL cohort gate assertion fails after source-free tests pass; precise assertion requires logs/reproduction.
Evidence: https://github.com/alwansan/raf/actions/runs/42889557850 SHA 67a1b0f; unit tests pass, pinned CL download passes, real 190-record gate fails.
No T4 mouse/Unity overlap. No CI duplication. Next: obtain failing assertion from logs and reconcile real telemetry; preserve fail-closed gate.
