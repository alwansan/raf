# T5 isolated scope — 20261107T0145Z-T5-scheduled-release403-audit-8f31
origin: scheduled
base_sha: a1c0ef3aecc1cc3943f1cc3b31330e4081c6ffa7
issue_id: DELIVERY-PUBLISH-403
status: completed
intended_files: prompt/coordination/clients/T5/work/20261107T0145Z-T5-scheduled-release403-audit-8f31.md; prompt/coordination/clients/T5/sessions/20261107T0145Z-T5-scheduled-release403-audit-8f31.md
experiment_key: release403-42296450023-gh-release-create-GITHUB_TOKEN-contents-write
resource_key: none (read-only GitHub API inspection)
taken_over_from: prior T5 publish-403 session ce57a58ab5ee996efed89d212e376222b96cf160
hypothesis: failure is a GitHub integration authorization boundary, not a Unity reconstruction failure; do not blindly add contents:write or rerun Unity.
Evidence: https://github.com/alwansan/raf/actions/runs/42296450023 reconstruct success, publish-early-test failure, delivery-result failure; previous T5 extracted HTTP 403 Resource not accessible by integration from gh release create with Contents:write already granted. Latest checked branch head a1c0ef3aecc1cc3943f1cc3b31330e4081c6ffa7. Recent run 42308935364 failed only in regenerate-from-current-ledger, a distinct issue; 42318375479 and 42318366901 succeeded.
Next: inspect release permissions/policy with owner-authorized credentials and attempt publication from retained verified delivery artifacts only if permissions permit; preserve signed checkpoint. Independently prioritize three right-side buttons and existing Resolution implementation after checking active T5 scopes. Do not launch duplicate native build.
