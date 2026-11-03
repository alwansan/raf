# Raft APK build readiness

Updated: 3 November 2026. Review baseline: 5e0fabb6d4009e04d8d5e420538609f8324f9fb8. Refresh live HEAD and Actions before every decision.

**State: NOT_READY.** No new native request/run has been created by this readiness setup. A final build candidate SHA has not yet been selected.

The owner's latest direction creates **Raft — جاهزية وبناء اللعبة**, a separate hourly readiness/build task. It records unresolved problems here, closes them with evidence, and starts the existing full delivery pipeline when all actual pre-build source/resource blockers are resolved and a phone trial is the next useful step. Existing recovery tasks continue their independent work. Pending device acceptance alone is not an impossible prerequisite for producing the device-test build.

## Persistent issues and evidence

| ID | Current classification | Evidence/current understanding | Required next evidence/action |
|---|---|---|---|
| WATER-001 | OPEN — source/resource blocker | Authentic UltimateWater shader/compute restoration and Unity kernel identity remain incomplete; strict water gate is false. Forty numeric table cases and194,887 checks passed, but do not execute translated shaders or the two-pass water pipeline. [Numeric report](ORIGINAL_BUTTERFLY_NUMERIC_2026-11-03.md), [FFT history](ORIGINAL_WATER_LFS_COMPUTE_INVENTORY_2026-11-03.md). | Restore genuine programs and bindings/GUID/pass contracts; validate numeric/format/selector behavior with suitable pre-build evidence. Do not change the gate merely to get a build. |
| RENDER-002 | OPEN — reported graphics defects, source closure incomplete | APK80 photos/logs show missing colours and broken effects. Original resource payloads and several shader families have verified recovery, but custom water/material/pass completion is not established. [Device feedback](WORK_SESSION_HANDOFF_2026-11-02_DEVICE_FEEDBACK_ACTIVE.md). | Map each remaining material/effect failure to its program/resource and record restoration/compatibility checks. Preserve content and quality. |
| DISPLAY-003 | SOURCE_REVIEW_REQUIRED; device acceptance pending | Desktop Settings resolution setter is guarded on Android. Dynamic timing repair passed23 executable checks and original managed compilation. Exact Settings-only aspect cause is not fully established. [Display audit](ORIGINAL_ANDROID_DISPLAY_AUDIT_2026-11-03.md). | Review the complete Settings/open/load/UI/display path; document remaining pre-build defects versus checks that genuinely require the phone. |
| AUDIO-004 | SOURCE_FIXES_VALIDATED; integration review/device acceptance pending | Version-aware OBB bank lookup and missing-event guards have source/managed evidence. Original banks are authenticated. No newer phone audio result. [Archive/audio report](ORIGINAL_ARCHIVE_AND_PLAYER_AUDIO_2026-11-03.md). | Confirm candidate bank staging/loading and narrow player/scene initialization contracts; retain sound/startup tests and list actual audible checks for the phone. |
| LOCAL-005 | SOURCE_FIXES_VALIDATED; integration review/device acceptance pending | Local RPC/identity and player-start source checks pass; APK80 host-wait feedback predates these fixes. Do not fabricate WorldHasBeenRecieved or hide failure. | Review actual create/load/local-host/save/resume path and real .rgd preservation; ensure no known source blocker remains, then list the single-player trial sequence. |
| INPUT-006 | SOURCE_TESTED; device acceptance pending | LEFT Mouse0 correction,500ms hold, Xbox overlay and physical-device ownership have source/managed checks. Twenty-two gesture and53 mapping checks passed. | Verify candidate action/UI binding and layout persistence checks remain green; phone checks cover menus, gameplay, drag, multitouch and external devices. |
| PERF-007 | SOURCE_REVIEW_REQUIRED; device acceptance pending | Historical phone GPU-memory OOM is real; it is not a result from later resource/lifetime/compression fixes. No new memory/FPS trial exists. | Audit current large allocations/formats/lifetimes and credible memory budget; classify remaining measurable runtime checks explicitly. Do not force a quality reduction as a substitute. |

Statuses are not blanket claims of completion. On each review add new defects and stable IDs; preserve closed rows with their fixing SHA, exact test/run evidence and remaining device checks. A row marked SOURCE_REVIEW_REQUIRED must be assessed and classified before readiness can be declared. Build failures get their own persistent BUILD-* rows with run_id, run_attempt, first failing job/step, cause and repair evidence.

## Decision and state transitions

1. NOT_READY: one or more concrete source/resource defects or required reviews remain. Record work and continue independent fixes; do not request a full build for a partial batch.
2. READY_FOR_BUILD: select immutable candidate_source_sha; link all appropriate checks to that code revision (or prove later changes are docs only). Close all known pre-build blockers with evidence. Keep honest DEVICE_TEST_PENDING entries. Recheck live HEAD and every nonterminal full-delivery/Unity experiment run.
3. BUILD_REQUESTED / BUILDING: create exactly one request using the existing protocol, record request_id, request commit SHA, run_id/run_attempt, URL and time. Preserve queued/running work and avoid equivalent requests.
4. BUILD_FAILED: identify the first real failure; repair and test its cause before one justified retry. A cancelled/timeout status requires diagnosis, not an invented cause or an unbounded retry loop.
5. AWAITING_DEVICE_TEST: complete signed APK+OBB+XAPK delivery exists and all delivery checks pass. Record exact files, hashes and links, installation instructions and phone test list. Repeated checks do not rebuild the same delivered candidate.

## Existing delivery system to reuse

Read [native operations](NATIVE_WORKFLOW_OPERATIONS.md), [complete delivery](WORK_SESSION_HANDOFF_2026-11-02_COMPLETE_DELIVERY.md) and [installation](ANDROID_INSTALL_AR.md), plus the live workflow and packaging code.

- Main workflow: .github/workflows/raft-unity-editor-android-import.yml; Unity2021.3.45f2, ARM64 IL2CPP, split/fidelity.
- Existing trigger: .github/raft-native-build-request.json with unique request_id, reason, requested_from_sha from the pre-request HEAD; request commit uses the two native/device-test markers documented in native operations. A supported native dispatch is an alternative. No native request is changed by this setup.
- Preserve source/scene/GUID/data/FMОD/signature checks, complete APK+OBB+XAPK and lossless transport parts/SHA manifests when required. XAPK is not APKS. Match actual release asset names/sizes/hashes and require successful delivery-result.
- Before packaging, existing artifact **raft-android-signed-output-checkpoint** retains audited signed APK and OBB. Existing **raft-android-audited-output-recovery** retains outputs after packaging failure. Reuse valid matching outputs to fix packaging/delivery without repeating Unity when feasible. Record artifact expiration and recover promptly; never claim a checkpoint exists until Actions confirms it.
- Keep cancel-in-progress:false, queue:max and engine serialization. If only a long wait remains, checkpoint run/status/next action and check in the next cycle.

## Build ledger

| Item | Current value |
|---|---|
| Readiness task | Raft — جاهزية وبناء اللعبة; enabled, hourly at minute55 Asia/Baghdad |
| candidate_source_sha | Not selected — NOT_READY |
| New request_id / request commit | None |
| New native run_id / attempt | None |
| Recovery artifact | None for a new candidate; verify per run |
| Last delivered game baseline | APK80, source9462f8edd8cdb5becbccb96521f2876ef9924410, tagandroid-early-test-41448086401-1; separate from lograf releases |
| Next review | WATER-001/RENDER-002 and classification of DISPLAY-003/PERF-007, followed by candidate-specific integration evidence |

The coordinator maintains this ledger, prompt/STATUS.md and the latest handoff after meaningful results. The reusable prompt is updated when directions change. Preserve concurrent work using live reads and expected-SHA leases.


## Readiness review — 3 November 2026

Reviewed live HEAD ee1be1d424f5b02f5bfdcca6db9c635ef85bbd6a and repository Actions: no queued/in-progress runs at review. Game release android-early-test-41448086401-1 still points to9462f8edd8cdb5becbccb96521f2876ef9924410 and has11 assets; CL raft-log root hashes remain unchanged. No new candidate or native request was selected. WATER-001 and RENDER-002 remain OPEN; numeric table validation does not close authentic shader/kernel restoration.

Executed local water-contract, delivery-package and native-workflow-isolation fixtures:25 tests ran successfully with1 skipped. These are test-owned/source-level fixtures, not an audit of a new APK or restored GPU programs. State remains NOT_READY. Next close WATER-001/RENDER-002 and complete DISPLAY-003/PERF-007 source reviews; device-only acceptance remains separate.



## WATER-001 typed SPIR-V image-contract probe — 3 November 2026

Source-only engineering commit [c1ba4a74](https://github.com/alwansan/raf/commit/c1ba4a74d79342998b40697b072b0216356f842c) added a fail-closed numeric OpTypeImage/OpTypeSampledImage → pointer → decorated variable parser. It records sampled scalar width/kind, dimensionality, multisample/array, declared image format and optional access qualifier for each bound SPIR-V image, with no private shader names or code. It compares this declared contract for each authentic FFT DXBC → SPIR-V → HLSL → SPIR-V candidate. Nine independent synthetic test cases passed locally; the new pre-LFS test step in [CPU-only audit41560719688](https://github.com/alwansan/raf/actions/runs/41560719688) also passed, but authenticated 20-program analysis was still RUNNING at this checkpoint. Treat actual format results and cross-roundtrip match as pending, not passed. This changes no original resources, Unity code or compute programs. WATER-001/RENDER-002 remain OPEN; NOT_READY, no native request.
