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


## First real isolated CI result and unrelated fixture repair
Sourcec4bbf346: new sidecar41434836582/job125241963213 COMPLETED SUCCESS without a Unity/native run. Runner41434836338 SUCCESS. Platform41434836349 FAILED at recently added actual touch-drag harness compilation: CS0060/CS0051 because synthetic MonoBehaviour, pointer interfaces, PointerEventData and overlay double were internal while the extracted actual authored handle remained public. This is harness accessibility, not original game CSharp failure. Correct doubles to public as actual Unity API types are; preserve the actual extracted runtime class. Targeted platform rerun requested by source fix; no native JSON/markers touched.
Existing hourly automation updated successfully/enabled with dedicated request paths, no duplicate/cancel loops, separate unit/private lanes, full-delivery result requirement and verified Release files. Active41419971187 remains immutable and running. This CI result is not a new APK.


## Verified isolation and repair checkpoint
New source isolation sidecar41434836582 COMPLETED SUCCESS; no Unity/LFS/license step, no native run entered delivery queue. Harness accessibility repair15966478: platform41435151202/job125242983468 COMPLETED SUCCESS, including actual extracted drag pointer-capture body and prior binding lifecycle, delivery/original-data/scene policies and offline build/smoke. This fixes test doubles only, not runtime game source. No new primary native run was generated by either code/test commit, confirming narrowed request-only triggering in practice.
Existing enabled hourly automation was updated with exact delivery/experiment request paths/schema/markers and no duplicate/cancel policy. Active41419971187/job125192945569 remains IN_PROGRESS at real Unity import/compile on immutable older1eaa2465. Do not cancel it, dispatch an experiment alongside this legacy run, or create another full native request while it works. Next inspect its actual APK+OBB/XAPK/release outcome; if missing, diagnose actual failing stage before one deliberate request. Current refactor's reusable native/experiment runtime has not been re-executed end-to-end; those jobs will be validated by the next justified native request, not by a duplicate test build now.


## 2026-11-02 — interrupted touch editor mode transition (independent source fix)
- Confirmed active full native 41419971187/job125192945569 still importing Unity assets from immutable 1eaa2465; did not cancel, restart or request a duplicate native build. Current source HEAD before this change 1ed0916a8dbfce1a417e61b3eacb72414f2c0102. CL lf/logfox/img directory indexes still show historical 2026-11-01 phone evidence only.
- Source-proven gesture gap: AndroidTouchLayoutHandle retained activePointerId if the editor was toggled off/on without OnPointerUp or OnDisable. SetLayoutEditMode previously toggled OnScreenControl components, not layout handles, so a stale finger could block a new drag. Clear all layout handle captures only on edit-mode transitions, before enabling the new mode. OnDisable shares the same cancel method; no stale pointer commits position.
- Extended the actual authored C#9/.NET8 drag-handle harness to reject stale drags/saves and accept a fresh finger after an interrupted edit-mode transition. Added source contract asserting SetLayoutEditMode invokes capture cancellation before changing mode. Source assertions were checked before commit; full dotnet harness and platform CI must be verified after push. No original game source, input actions, .meta/GUIDs, FMOD, graphics, scenes, .rgd or delivery workflow changed. No new native build request.
- Next: inspect targeted platform CI for this source; inspect actual completion of active native and APK+OBB/XAPK Release. A passing harness does not establish Unity EventSystem or physical multitouch behavior on POCO F5 Pro.


## Verified interrupted-mode pointer fix — 2026-11-02 15:10 Baghdad
- Commit 6d05360a9a1145d49157ffa644b46c7f2ca36b7d updated authored AndroidTouchLayoutHandle and SetLayoutEditMode: reset stale captured pointer on edit-mode transitions; no original game source/asset changes, no native request marker.
- Real cheap Android platform CI https://github.com/alwansan/raf/actions/runs/41442295297 completed SUCCESS at 12:09:28 UTC. Actual extracted C#9/.NET8 drag harness reported RAFT_TOUCH_DRAG_CAPTURE checks=15, conflictingTouchesIgnored=true, duplicateSaves=0; netstandard2.1 compilation reported 0 errors, platform policies and offline smoke passed. This is managed CI, not Unity EventSystem or phone touch acceptance.
- Original-source offline integration https://github.com/alwansan/raf/actions/runs/41442295333 was still in progress at the checkpoint. Full native https://github.com/alwansan/raf/actions/runs/41419971187 remains in progress on immutable older 1eaa2465 at Unity import; no duplicate Unity run or new APK requested. CL/raft log still contains only the historical 2026-11-01 LF/logfox/screenshots.
- Next: verify offline integration final result and full native packaging/publisher. If native fails, diagnose first real failure; if it succeeds, confirm Release APK+OBB/XAPK asset names, sizes and hashes. Only then consider one new native request for accumulated verified Android touch fixes. Physical gameplay, water, FMOD and .rgd still require evidence.


## Confirmed full native delivery failure and permission repair — 2026-11-02
- Refreshed HEAD52cb96d4 and live Actions: full native41419971187/job125192945569 COMPLETED FAILURE at12:25UTC (15:25 Baghdad). Historical IN_PROGRESS statements above are superseded. Unity step40 SUCCESS, APK structure/original StreamingAssets/FMОD and signature gates SUCCESS; package step46 FAILURE, retention/publication skipped, zero retained artifacts. This was not cancellation, Unity compilation failure, licensing failure or phone GPU OOM.
- Direct large-log connector twice failed with transport closed. Added independent no-Unity/no-LFS read-only delivery diagnostics. First41447389494 failed because current gh requires --allow-escape-sequences for ANSI logs even when redirected; fixed only the private file download. Diagnostics41447497169/job125284126908 SUCCESS recovered bounded authored packaging evidence. Exact terminal exception: PermissionError: [Errno13] Permission denied: 'builds/delivery'. Twelve packaging fixtures had passed immediately before it. Actual markers: native resultSucceeded/errors9/bytes6764190595; OBB2301233974bytes; signature verifiedtrue. Native success does not establish graphics/audio/gameplay;9BuildReport diagnostics remain, not silently cleared.
- Repair: construct complete delivery under runner-owned RUNNER_TEMP/raft-android-delivery and retain from runner.temp instead of creating a sibling under the container-produced builds directory. Input APK/OBB untouched; no sudo/chmod/chown, size reduction, missing resources or bypassed audits. Exact ownership/mode of the now-disposed builds directory was not captured; write denial itself is confirmed, container ownership is the likely mechanism.
- Add recovery artifact ONLY when the already-audited packaging step actually fails: exact APK+matching OBB, compression0,2days, no reconstructed sources/assets/secrets. It does not bypass publication or final delivery-result; a packaging failure remains a failed delivery. This prevents another validated build from disappearing solely due to downstream packaging.
- New regression executes the actual packaging shell commands with synthetic APK/OBB and a non-writable builds parent. Old output must fail PermissionError; runner-temp output must succeed with exact APK/OBB bytes, installer instructions and reassembler; retention paths/recovery scope checked. Local12package+8isolation+6distribution tests passed; permission scenario skipped locally because runtime uid0 bypasses filesystem mode checks. MUST verify it executes unskipped under actual non-root Actions runner before requesting full Unity. No new full native request in this repair commit.
- Prior touch fix6d05360a: both41442295297 and41442295333 now SUCCESS. CL lf/img/logfox indices checked: same3historical sessions,15screenshots,4logfox files; no new phone evidence. Only feature/android-native-port modified.
- Next: inspect real cheap repair CI; if permission regression passes and no heavy job active, submit ONE dedicated native build request for full APK+OBB/XAPK delivery with current tested touch fixes. Main request schema/markers and workflow isolation unchanged. Continue Singleplayer/water/compute/.rgd/FMОD acceptance independently; no owner dependency action needed.
