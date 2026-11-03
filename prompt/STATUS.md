# Current Raft checkpoint — 3 November 2026

Read [current owner requirements](../docs/CURRENT_OWNER_REQUIREMENTS.md), [AGENTS.md](../AGENTS.md), then the [latest full handoff](../docs/WORK_SESSION_HANDOFF_2026-11-03_LEFT_TOUCH_AND_RESUME.md). This file is a concise checkpoint; refresh live HEAD, Actions and concurrent changes before writing.

## New readiness/build coordinator

**Raft — جاهزية وبناء اللعبة** is created/enabled, hourly at minute55 Asia/Baghdad. It maintains [APK_BUILD_READINESS.md](../docs/APK_BUILD_READINESS.md), currently **NOT_READY**, and uses the existing full APK+OBB+XAPK system after actual pre-build source/resource blockers are resolved and device testing is the next useful step. It diagnoses/repairs build errors and recovers signed checkpoints for packaging failures. The two recovery tasks remain unchanged. No new native request/build was made. This coordinator-specific direction supersedes earlier blanket build-hold wording; source/recovery work continues independently.

## Latest verified result: original FFT numeric reference

Source d57d00a94826508608bd21b8d34b793d0ff4ba7f; [original-source CPU numeric CI41555453779](https://github.com/alwansan/raf/actions/runs/41555453779), job125653301781, **SUCCESS**. Executes the original butterfly utility, original GPU-table encoding body and original CPU FFT stage body with three SHA pins. For sizes32/64/128/256/512:40 packed-table cases,20 original CPU signal comparisons,194,887 checks; three deliberately wrong stage/sign/normalization controls detected. Max relative-L2 errors: full-float replay1.8894e-7; table-only binary16 replay2.3869e-4; original CPU lane2.0495e-7. Local21 related Python tests passed. [Full report and limits](../docs/ORIGINAL_BUTTERFLY_NUMERIC_2026-11-03.md).

This does not execute original/translated GPU programs, Unity, two-dimensional water or all CPU channel layouts. Table replay uses double intermediates; actual half render-target rounding is untested. Supplied integer stage counts do not settle original Mathf.Log rounding. Strict water authenticity gate remains **false**.

## Prior verified evidence retained

- Stored quality object6376/resources.assets:476bytes, exact object/four schema-source hashes locally verified. Source-corroborated layout yields caps32,64,256,512,512,256,256; synchronization with Unity enabled. Saved index6 is not active-phone proof. Full custom TypeTree remains unverified. [Resource41554294910](https://github.com/alwansan/raf/actions/runs/41554294910), [schema-source41554501052](https://github.com/alwansan/raf/actions/runs/41554501052), [synthetic decoder41554799751](https://github.com/alwansan/raf/actions/runs/41554799751) SUCCESS. [Quality report](../docs/ORIGINAL_WATER_QUALITY_VALUES_2026-11-03.md).
- Constructor size traces through the typed WindWaves int property/backing field to the minimum of requested resolution, quality cap and device texture limit: [41553441187](https://github.com/alwansan/raf/actions/runs/41553441187) SUCCESS. Inherited selector seed: [41548942077](https://github.com/alwansan/raf/actions/runs/41548942077) SUCCESS. Original20-slot resource/name/two-pass dataflow: [41551173277](https://github.com/alwansan/raf/actions/runs/41551173277) SUCCESS. [Authentic FFT history](../docs/ORIGINAL_WATER_LFS_COMPUTE_INVENTORY_2026-11-03.md).
- Android missing early fall-event guards: c22ebf30/[41551991560](https://github.com/alwansan/raf/actions/runs/41551991560) SUCCESS,10 executable cases and original managed compile exit0. Dynamic-resolution invalid GPU-timing guard: fb0cdc20/[41552985664](https://github.com/alwansan/raf/actions/runs/41552985664) SUCCESS,23 checks/10 cases and managed compile exit0. Settings-aspect cause and actual phone audio/world remain open.
- LEFT touch source6aafa9f4: [platform41548465582](https://github.com/alwansan/raf/actions/runs/41548465582) SUCCESS (22 gesture checks,53 extracted-method mouse checks); [original managed41548465622](https://github.com/alwansan/raf/actions/runs/41548465622) SUCCESS. No Unity/device input loop proven.
- Six owner-supplied archive parts inspected; original banks and managed DLL hashes match tracked/pinned data. Authenticated local resources.assets111533516bytes SHA87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c restored from archive; reuse before duplicate LFS. [Archive evidence](../docs/ORIGINAL_ARCHIVE_AND_PLAYER_AUDIO_2026-11-03.md).

## Current constraints and next work

Only feature/android-native-port writable; CL read-only. Full native delivery is coordinated through [APK_BUILD_READINESS.md](../docs/APK_BUILD_READINESS.md) and the separate readiness task after its evidence conditions are satisfied; source/recovery tasks do not independently start Unity/native work. Preserve original assets/.meta/GUID/.rgd. LEFT MouseButton.Left/Mouse0,500ms; automatic touch-to-mouse=false; preserve UGUI/controller/physical input. Ignore unavailable الجلسة1.txt/text.txt. Both recovery tasks remain configured; the new readiness/build coordinator is separate. Preserve all tasks and avoid duplicates.

Last game delivery: APK80/source9462f8edd8cdb5becbccb96521f2876ef9924410, tagandroid-early-test-41448086401-1,11assets verified. Newer lograf releases are separate. Current CL raft-log roots unchanged. Later source fixes are not installed-phone evidence.

Next: use the numeric reference to compare actual translated original DXBC/SPIR-V arithmetic/output, typed image formats, stages and both passes; also establish serialized per-water requested resolution/scene linkage and active quality/device limits. Do not infer runtime kernel enumeration from serialized20-slot order or ship dummy/clamped kernels. Continue independent genuine fixes where evidence supports them. Update this checkpoint and full handoff after meaningful work; update [copy-ready resume prompt](CONTINUE_RAFT_AR.md) when directions change.


## Readiness review — 3 November 2026

Reviewed live HEAD ee1be1d424f5b02f5bfdcca6db9c635ef85bbd6a and repository Actions: no queued/in-progress runs at review. Game release android-early-test-41448086401-1 still points to9462f8edd8cdb5becbccb96521f2876ef9924410 and has11 assets; CL raft-log root hashes remain unchanged. No new candidate or native request was selected. WATER-001 and RENDER-002 remain OPEN; numeric table validation does not close authentic shader/kernel restoration.

Executed local water-contract, delivery-package and native-workflow-isolation fixtures:25 tests ran successfully with1 skipped. These are test-owned/source-level fixtures, not an audit of a new APK or restored GPU programs. State remains NOT_READY. Next close WATER-001/RENDER-002 and complete DISPLAY-003/PERF-007 source reviews; device-only acceptance remains separate.
