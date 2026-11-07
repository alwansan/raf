# T5 scheduled session 20261107T0246Z-T5-scheduled-release-permission-matrix-6a91
origin: scheduled
base_sha: 942aba28c9e13ecb0269023a307645c0b1828ac5
scope_commit_sha: 5fa2401ea3869daec6dadbdda8669f99aadaefc6
work: prompt/coordination/clients/T5/work/20261107T0246Z-T5-scheduled-release-permission-matrix-6a91.md
resumed_from: 20261107T0145Z-T5-scheduled-release403-audit-8f31.md; 20261106T2025Z-T5-chat-early-unity-editor-abi-7e2f.md

## Immutable evidence, 2026-11-07 02:46 UTC
- GitHub API run 42296450023: head a1737bd736e276d53df808442cfae3b1eea0d488, event push, completed failure. Jobs: native-request-gate 128162826762 success; unity-license-preflight 128162973182 success; reconstruct 128163021015 success; publish-early-test 128223516997 failure at 'Publish complete APK OBB XAPK packages and lossless transport parts'; delivery-result 128223950495 failure at gate.
- Earlier T5 job-log investigation recorded gh release create HTTP 403 'Resource not accessible by integration', despite workflow Contents:write. This is not proof that the artifact itself is malformed.
- Repo releases API returned github-actions[bot] as author for lograf-89 (published 2026-11-05 19:55:21Z), lograf-88, lograf-87, lograf-86 and lograf-84. Thus this repository has successfully published releases via an Actions bot in another workflow; a repository-wide unconditional ban on all bot-created releases is not supported. **It does not prove the native workflow token has identical effective permissions or tag restrictions.**
- Latest branch HEAD at read: 942aba28c9e13ecb0269023a307645c0b1828ac5; recent workflow 42329314154 completed success (T3), no new Unity build initiated. Report docs/DEVICE_FEEDBACK_42058825739_AR.md read first; its world/save/re-entry result is limited to artifact 42058825739.

## Diagnostic decision
New discriminating finding: release-create failure is context-dependent rather than an unconditional repository-wide ban. Check native publish job's actual effective token scope and ref/tag policy, compare with lograf release job identity, branch event and release tag, and use an isolated permission preflight before retrying release; do not rerun Unity. A 403 alone does not distinguish workflow token scope from tag/ruleset restrictions or app-installation restrictions. No API mutation to releases, no token disclosure.

## Limits and next
No APK/OBB device hash attestation, no LogRaft device benchmark, no UI/Resolution/mouse code change. T4 owns physical mouse. T5 next: inspect native and lograf workflow release permission differences and ruleset evidence; after coordination implement three right-side buttons and Resolution change separately, with safe-area regression tests. No claim of game READY: NOT_READY 0/3.
status: completed (narrow release-permission hypothesis audit); release issue OPEN
