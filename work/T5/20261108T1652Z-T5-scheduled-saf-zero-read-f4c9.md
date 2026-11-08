# T5 work — 20261108T1652Z-T5-scheduled-saf-zero-read-f4c9
origin: scheduled
session_id: 20261108T1652Z-T5-scheduled-saf-zero-read-f4c9
issue_id: DELIVERY-013
status: waiting_ci
base_sha: 239d12d3bf826daa3051bd3b3b66abfe689b6962
hypothesis: A broken SAF ContentProvider can repeatedly return zero bytes from InputStream.read(byte[]) and hang StreamSha256 indefinitely, without interrupt or progress; existing test suite has no zero-read case.
intended_files:
- apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/StreamSha256.java
- tests/java/T5StreamSha256Test.java
- work/T5/20261108T1652Z-T5-scheduled-saf-zero-read-f4c9.md
- prompt/coordination/clients/T5/sessions/20261108T1652Z-T5-scheduled-saf-zero-read-f4c9.md
experiment_key: t5-saf-zero-read-stall-jdk17-source-239d12d3
resource_key: none (source-only; no Unity or Android build)
updated_at: 2026-11-08T16:53:30Z
coordination: T4 owns mouse click/capture; no shared host MainActivity edits. No equivalent in-flight T5 test known; source workflow is paths-scoped and non-cancelling.

implementation_commits: 869ba255b85d8b9cd258efd618106c1562597d23, 8b98dff0d371486aab03e3aae56f2422c1ad7a05
validation_run: https://github.com/alwansan/raf/actions/runs/42502155293 (in_progress at last check)
next: inspect result and fix only if failing; no duplicate CI or Unity build.
