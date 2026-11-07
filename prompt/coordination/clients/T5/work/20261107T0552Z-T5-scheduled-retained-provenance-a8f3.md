# T5 independent work 20261107T0552Z-T5-scheduled-retained-provenance-a8f3
origin: scheduled
baseline_sha: 7e607e44942aca3b61d4c616c14a204ef63a4c5b
issue: INTEGRATION-001 / delivery retention
files: prompt/coordination/clients/T5/work/20261107T0552Z-T5-scheduled-retained-provenance-a8f3.md; prompt/coordination/clients/T5/sessions/20261107T0552Z-T5-scheduled-retained-provenance-a8f3.md
hypothesis: owner-tested 42058825739 delivery may already have a retained copy, so expiry of original signed checkpoint is not equivalent to loss of the entire tested package.
experiment_key: t5-retained-artifact-42110297871-20261107
shared_resource: none; read-only GitHub API; no Unity or release dispatch
collision_policy: metadata-only independent of T4 mouse and other T5 code changes; do not modify shared files.
next: check exact retained package provenance and archive digest versus signed checkpoint; avoid equating outer ZIP digest with APK or OBB SHA.
