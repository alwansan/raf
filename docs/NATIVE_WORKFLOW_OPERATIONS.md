# Native build, light preflight and experimental lanes

Only feature/android-native-port is writable. Keep Unity2021.3.45f2 and existing data/signature/scene gates.

## Dedicated workflows
- raft-unity-editor-android-import.yml: full ARM64 Unity build + APK/OBB/XAPK delivery. Normal code, shader, docs or test commits MUST NOT start this workflow. Automatic push entry only watches .github/raft-native-build-request.json. Dispatch mode is native only and delivery defaults true.
- raft-reconstruction-preflight.yml: prior reconstruction synthetic fixtures, without Unity, activation environment or LFS downloads. It has its OWN concurrency group. Existing platform/original-source/diagnostic test workflows remain separate.
- raft-unity-android-experiment.yml: separately named private native experiment, reusing reviewed main build jobs instead of maintaining a divergent1000line copy. Dedicated experiment request/dispatch and private lane; public release disabled. Actual future Editor jobs across lanes share a queue:max engine mutex to avoid license contention. Never use experiments merely to bypass an active/failed release build.

## Why the old queued run was cancelled
41403797736 created07:03:17UTC, cancelled08:35:20UTC, ZERO jobs.
41414168826 created08:35:19UTC on the SAME old workflow/group.41400935501 was still running until08:56UTC.
This timing and0job state match GitHub's default pending replacement: cancel-in-progress:false protects the running item, but queue:single replaces an existing pending item. Actor/triggering_actor identifies the starter, not who cancelled; do not invent manual-canceller identity.
Primary reference:
https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
queue:max now preserves up to100pending items with cancel-in-progress:false. It is defensive; DO NOT fill queues with redundant multi-hour builds.

## Request one delivery build
First inspect actual runs by workflow PATH (names can change), including queued/pending/in-progress items. If a full delivery/experiment is already active, record next source changes in the handoff; keep doing independent preflight work. Do not cancel, blindly rerun, or add duplicate requests. Wait for the current actual result before choosing the next build.

After meaningful source changes and passing cheap checks, create/update ONLY this request file for the deliberate native trigger:
.github/raft-native-build-request.json

Example:
{
  "request_id": "unique-new-request-id",
  "reason": "Validate the tested runtime/render fix and deliver complete install files",
  "requested_from_sha": "40-character-current-base-commit-sha"
}

Commit with BOTH [raft-native-build] and [raft-device-test]. Markers alone no longer start the main workflow; the dedicated request file must change. A missing/malformed request or wrong branch fails explicitly. Do not touch the request file for docs-only checkpoints or ordinary tests.

workflow_dispatch alternatively accepts build_mode:native and publish_early_test:true. Primary delivery requires real reconstruction+publication success. Activation unavailable, skipped build, absent APK/OBB, failed package/signature/data gates or skipped/failed release must not become a successful native delivery run.

## Request a private experiment
Use only for a concrete independent hypothesis that cannot be covered by cheap fixtures. Prefer the dispatch entry with a reason. If dispatch is unavailable on a non-default branch, create/update .github/raft-native-experiment-request.json with the SAME JSON schema and commit [raft-native-build] [raft-native-experiment] WITHOUT [raft-device-test]. Do not change the delivery request file simultaneously.
The experiment wrapper passes build_lane:experiment,publish_early_test:false to reusable build jobs. It does not enter or replace the delivery workflow queue. Future actual Editor work serializes on the engine mutex; a separate lane is not proof that concurrent Unity licensing is supported. Legacy active41419971187 predates the new engine mutex: do NOT start a heavy experiment alongside it.

## Delivery result and failure handling
Full main success requires:
1. Explicit valid branch/request.
2. Real Unity ARM64 output and all original40scene/SDK/shader/FMОD/bank/data/signature gates.
3. Complete APK+OBB/XAPK/transport parts and hashes retained and published.
4. Published release asset names/sizes match every local delivery file.
5. Final delivery-result job confirms reconstruction AND publication success.

Private experiment success requires an actual audited native build, but deliberately no public release. It is not a delivered user APK.

If the main build finishes without APK or complete delivery, inspect the FIRST actual failure, classify it (request/license/import/CSharp/shader/IL2CPP/Gradle/disk/package/transport/release), fix it and run targeted cheap checks before one justified next native request. Do not call preflight green a native success, and do not use repeated APK runs as a substitute for source recovery.

## Preserve active work
Do not modify main build configuration routinely. Edit it only for a demonstrated build/package/signing/publishing/orchestration defect or an explicit owner request. Unit tests and experiments belong to their lanes.
Keep cancel-in-progress:false,queue:max and separated groups. Never add cancel/retry loops or multiple overlapping scheduled developer tasks. The existing hourly task records follow-up changes and resumes after actual job outcomes.
If only a >10minute integration wait remains, persist exact run/status/next action and stop waiting. CI success is not phone graphics/audio/.rgd/touch/gameplay acceptance.
