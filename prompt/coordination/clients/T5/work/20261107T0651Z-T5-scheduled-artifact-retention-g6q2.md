# T5 scoped work 20261107T0651Z-T5-scheduled-artifact-retention-g6q2
origin: scheduled
baseline_sha: 13c36d0b57dc64f74b8b04469f56c99dae6a6049
issue: INTEGRATION-001 / time-critical native artifact retention
files: prompt/coordination/clients/T5/work/20261107T0651Z-T5-scheduled-artifact-retention-g6q2.md; prompt/coordination/clients/T5/sessions/20261107T0651Z-T5-scheduled-artifact-retention-g6q2.md
hypothesis: original signed checkpoint expires earlier than retained delivery; validate current live API metadata before treating any backup as durable or equivalent to signed APK/OBB.
experiment_key: t5-artifact-retention-20261107T0651Z
shared_resource: none; GitHub API read-only; no Unity, release, CI dispatch or T4 mouse overlap.
taken_over_from: prompt/coordination/clients/T5/sessions/20261107T0552Z-T5-scheduled-retained-provenance-a8f3.md
next: verify live artifact expiration and digest, preserve exact identity limits; prioritize durable retention before expiry.
