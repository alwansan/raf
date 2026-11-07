# T5 work scope — 20261107T0350Z-T5-scheduled-artifact-expiry-c8e4
origin: scheduled
baseline_sha: 6c19f46efd9d9ca91747960171c89166093ba225
issue: DELIVERY-001
experiment_key: t5-signed-artifact-expiry-42296450023
files: this work file; clients/T5/sessions/20261107T0350Z-T5-scheduled-artifact-expiry-c8e4.md
hypothesis: successful reconstruction output remains recoverable despite release HTTP403, but short artifact expiry is a concrete delivery risk.
shared_resource: GitHub Actions artifacts read-only; no Unity or release mutation.
coordination: T4 physical mouse remains separate; no T1–T3 shaders touched. Do not duplicate build or release.
result: API metadata read of run 42296450023; signed checkpoint id 13550196498 expires 2026-11-09T23:48:15Z, delivery id 13549514149 expires 2026-11-09T23:49:06Z; both expired=false at 2026-11-07T03:50Z. Metadata does not prove APK/OBB integrity. Follow-up: owner/authorized release actor should preserve artifacts before expiry, validate signed manifest hashes, investigate 403 token/tag policy; no automatic bypass.
status: completed (bounded metadata evidence)
