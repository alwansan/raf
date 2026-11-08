# 20261108T1255Z-T5-scheduled-artifact-download-limit-q9r2
origin: scheduled
issue_id: DELIVERY-ARTIFACT-42058825739
base_sha: d9b9267d405868b2a528cd875661df7a2b3a439f
intended_files: prompt/coordination/clients/T5/work/20261108T1255Z-T5-scheduled-artifact-download-limit-q9r2.md; prompt/coordination/clients/T5/sessions/20261108T1255Z-T5-scheduled-artifact-download-limit-q9r2.md
experiment_key: github-connector-download-artifact-13454900880-max536870912-vs5948243834
resource_key: none (read-only connector, no Unity)
status: blocked
updated_at: 2026-11-08T12:55:00Z
hypothesis: Connector download may provide durable binary handoff before expiry.
result: Attempted mcp__GitHub__download_workflow_artifact on 13454900880; failed InvalidInputException: Artifact exceeds max size of 536870912 bytes: 5948243834 bytes. This rules out this connector path; archive itself was not downloaded, and no private durable copy was made.
next: Use an authorized runner/gh API with >=6GB available disk and private destination; verify outer archive digest and individual APK/OBB SHA256; avoid public raw game assets.
