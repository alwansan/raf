# Workflow isolation and pending cancellation — 2026-11-02

Owner explicitly requests isolating cheap tests and optional experiments from the primary full Unity/APK/OBB/XAPK workflow, preventing accidental pending replacement, updating the existing scheduled developer task and treating missing delivery as failure.

## Actual investigation
Entry HEADa67e337aba3bf780e30756d17bc3b692c87893e0.
Selected41403797736: completed/cancelled; created07:03:17UTC,updated08:35:20UTC; jobs=[].
Replacement41414168826: created08:35:19UTC,same old workflow/group,sourcec7aafcce,ultimately preflight-only success. Running41400935501 continued until08:56UTC then FAILED packaging, not cancellation.
This is strong evidence of automatic pending queue replacement, not a Unity crash. The API actor account does NOT identify a manual canceller. No cancellation API call was made by this engineering session.
GitHub documentation confirms queue:single default replacement even with cancel-in-progress:false, and queue:max support up to100pending:
https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency

## Implemented
Read docs/NATIVE_WORKFLOW_OPERATIONS.md for exact entry points and request schema.
- Primary workflow automatic push trigger narrowed to dedicated .github/raft-native-build-request.json. Kept explicit native/device authorization and protected branch; dispatch now native-only/publish-default-true.
- Prior reconstruction unit fixture preflight moved to separate no-Unity/no-LFS/no-license workflow. Ordinary source/test/workflow edits do not enter main queue. Required integrity fixtures remain as early native safety gates too.
- Separate manual/dedicated-request private experiment wrapper reuses the same reviewed build jobs, separate workflow concurrency namespace, no public publishing. Future actual Unity jobs share a queue:max engine mutex for license/resource serialization.
- Main delivery mutex preserves existing name for the default lane, cancel-in-progress:false plus queue:max. No cancellation or duplicate native build requested; no initial request JSON created by this refactor.
- Explicit request/branch/schema gate. Missing activation now fails instead of green skip.
- Always-run final result rejects absent/skipped/failed native build and skipped/failed delivery; private experiment deliberately only requires audited build.
- After gh release create, query actual remote assets and require exact names/sizes for all published delivery files, recording verified release URL.
- Existing game source, scenes, metas/GUIDs, full-fidelity texture policy, real source/data/FMОD/signature gates remain unchanged.

## Tests and state
8local isolation tests pass: dedicated triggers, queue/group separation, private experiment, unit-only lane and EXECUTION of actual request/result/published-file gates against successful and failed/skipped/missing-data cases.6existing redistribution tests pass. YAML/bash and all embedded Python parsed.
Push first as cheap-CI-only change. Inspect the new sidecar and existing platform/runner checks; no real new native integration claimed.
Current41419971187/job125192945569 remains IN_PROGRESS on immutable1eaa2465, last observed Unity Editor import/compile. No currentAPK/release result yet. This refactor does not affect the active run or start a second one.
Update existing hourly scheduler with the dedicated-request protocol. After active result, inspect actual complete delivery; incorporate validated newer source once via a new request file+markers only if justified. No repeated user permission/dependency/license requests.
