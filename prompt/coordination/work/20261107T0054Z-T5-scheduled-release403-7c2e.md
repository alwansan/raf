# T5 scoped work — release HTTP 403

session_id: 20261107T0054Z-T5-scheduled-release403-7c2e
origin: scheduled
issue_id: DELIVERY-APK-OBB
status: completed_diagnostic
updated_at: 2026-11-07T00:54:00Z
intended_files: [this work record, prompt/coordination/clients/T5/sessions/20261107T0054Z-T5-scheduled-release403-7c2e.md]
experiment_key: release-create-403-run42296450023-job128223516997-source-a1737bd7
resource_key: none (read-only Actions logs; no Unity)
hypothesis: failed publish due to release creation authorization, not artifact integrity

## Direct evidence
Run https://github.com/alwansan/raf/actions/runs/42296450023 job https://github.com/alwansan/raf/actions/runs/42296450023/job/128223516997: download-artifact completed, 5,948,365,703-byte artifact sha256 885502613c39f8388b692b65cd7e33ad7b6c49783e83f705e31177d6b9a3c233. At 2026-11-06T23:51:18Z, gh release create returned HTTP 403 Resource not accessible by integration on POST /repos/alwansan/raf/releases. Runner GITHUB_TOKEN advertised Actions:read, Contents:write. Thus failure is at release API authorization, not at download, Unity reconstruction, or proved APK/OBB validation. Shell had prior Python validation, but no detailed success output for all files; do not claim device verification.

## Follow-up
Check GitHub App installation permissions and repo/org Actions token restrictions and whether the token is permitted to create releases; do not assume adding permissions:contents:write alone solves it because already granted. If owner permits, publish via a credential with releases permission or use checkpoint/artifact recovery, without rebuilding Unity; verify release assets against delivery.json. Do not expose tokens or retry identical failed release operation. UI/mouse/Resolution remains separate T4/T5 work.
