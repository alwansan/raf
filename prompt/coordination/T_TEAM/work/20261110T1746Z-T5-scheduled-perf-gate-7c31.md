# T5 scope 20261110T1746Z-T5-scheduled-perf-gate-7c31
origin=scheduled; baseline=f3ef5d8d29e365d98094378f70964a741d57f1dd
PERF-007: run 42849324096 skipped because redundant commit-message job gate despite path-filter match. Change only .github/workflows/raft-t5-cl-real-fps-cohort.yml; session file separately. T4 mouse files untouched. No shared Unity resource.
Hypothesis: removing redundant job if allows real regression tests to run on relevant push, retaining pinned CL inputs, timeout and concurrency. Test via ensuing workflow run. Evidence https://github.com/alwansan/raf/actions/runs/42849324096
