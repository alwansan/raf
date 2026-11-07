# T4 scheduled session — 20261107T0245Z-T4-scheduled-release-permissions-p4x8
origin: scheduled
identity: T4
baseline_sha: f0b88b20f43d9073c600d80ed83bd6770a9fd9c3
scope: prompt/coordination/work/20261107T0245Z-T4-scheduled-release-permissions-p4x8.md

## Verified evidence (2026-11-07 UTC)
- Owner phone feedback docs/DEVICE_FEEDBACK_42058825739_AR.md confirms actual world entry, save, exit and re-entry on run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628. Keep LOCAL-005 open; do not regress .rgd.
- Native run https://github.com/alwansan/raf/actions/runs/42296450023 source a1737bd736e276d53df808442cfae3b1eea0d488 has completed with conclusion failure. GitHub jobs endpoint independently confirms native-request-gate SUCCESS, unity-license-preflight SUCCESS, reconstruct SUCCESS, publish-early-test FAILURE at 'Publish complete APK OBB XAPK packages and lossless transport parts', delivery-result FAILURE at 'Refuse green native runs with missing build or delivery'. This is delivery-stage failure, NOT a Unity build failure.
- Previous T4 session 20261107T0135Z-T4-scheduled-release403-a6q9.md found workflow declares contents: write and uses RAFT_RELEASE_TOKEN when present, otherwise github.token. YAML permission declarations alone cannot prove effective installation/token rights; 403 root cause remains unproven.

## Diagnostic decision / next action for T5
Reuse signed checkpoint/delivery artifacts if still retained, without rebuilding. Inspect failed publish step's exact gh invocation and response, record workflow trigger/ref/repository policy and whether effective token is custom PAT or GITHUB_TOKEN **without printing token**. A safe preflight can use gh api repos/:owner/:repo/releases with same token and inspect HTTP status/headers; GET success does not establish POST rights. Compare token's scoped permissions/repo access and release restrictions; only retry publishing when a concrete policy/credential correction is proven. Do not blindly add contents:write again or bypass delivery-result gate.

## Input and phone acceptance boundary
Mouse pointer capture, Raft cursor, three physical mouse buttons, focus transitions, keyboard, fullscreen edge/system bars, and resolution need testing on a correctly matched signed APK+OBB. No device test or code fix performed here. T5 owns three UI buttons and Resolution. Preserve original world save proof and do not assert source fixes as device-confirmed.

## Result
Completed independent job-level classification of failure from live Actions jobs endpoint; source unchanged. No CI launched or cancelled. Next: T5 release authorization diagnosis and artifact recovery; T4 input device acceptance when installable matching package available. Full readiness remains NOT_READY until independently proven.
