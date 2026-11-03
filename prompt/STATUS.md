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



## Current engineering delta — 3 November 2026

[c1ba4a74](https://github.com/alwansan/raf/commit/c1ba4a74d79342998b40697b072b0216356f842c) adds typed-image numeric reflection for authenticated FFT SPIR-V and comparison after HLSL recompile. New source/tests/workflow changes only: no .meta, LFS payload, runtime shader, touch, native request or scheduled task mutation. Nine local synthetic integrity cases passed; the initial workflow test stage also passed. [20-program resource audit41560719688](https://github.com/alwansan/raf/actions/runs/41560719688) was in progress while three original SHA-verified LFS owners were hydrating. No authentic typed-image result or original GPU execution is claimed before its last stage. Maintain NOT_READY, WATER-001/RENDER-002 open; last full game delivery remains APK80/source9462f8e. Cross-check run and live HEAD on continuation; update evidence only after verified completion.


## Authenticated FFT typed image finding — final CI 3 November 2026

[c1ba4a74](https://github.com/alwansan/raf/commit/c1ba4a74d79342998b40697b072b0216356f842c) added name-free SPIR-V image declaration tracing; [first audit41560719688](https://github.com/alwansan/raf/actions/runs/41560719688) PASSED authentic20 programs and60 image declarations. New source [97b242ee](https://github.com/alwansan/raf/commit/97b242ee8a80aa7c5d8a76cf2b3fcbdba4e1031b) adds bounded per-binding difference reporting;12 synthetic tests passed locally and [final audit41561153253](https://github.com/alwansan/raf/actions/runs/41561153253) COMPLETED SUCCESS on the original SHA-checked LFS owners and20 variants.

All original modules declare three float32 2D image resources (sampled bindings0,1 and storage binding2) with SPIR-V format Unknown (enum0). After private HLSL50/glslang recompile, exactly one numeric field differs in all20: storage output at set0/binding2 becomes format_enum1 (Rgba32f); the other typed fields, bindings and workgroups are preserved. Strict water/Unity kernel identity remains false; this does not prove original RenderTexture format, GPU numeric correctness or on-phone water. Next verify actual original Unity render target format and resource creation/binding against this targeted drift, then numerical shader equivalence. NOT_READY, no Unity/APK started; phone evidence still only APK80. The existing three scheduled tasks were not changed.


## Runtime authenticated original FMOD bank guard — 3 November 2026

- Source [25624798](https://github.com/alwansan/raf/commit/25624798d1bda6ffcd7ae6e5e8300d59a2819f65) verifies the five independently authenticated original FMOD bank lengths/SHA-256 values **after APK/OBB byte reading and before** `StudioSystem.loadBankMemory`. An incorrect same-version OBB entry, truncated/replaced bank or unrecognized bank name now fails explicitly instead of being handed to FMOD. Does not replace bank bytes, events, platform provider or local-world logic.
- [Audio C# CI41561256404](https://github.com/alwansan/raf/actions/runs/41561256404) **COMPLETED SUCCESS**, 53 policy checks against existing managed providers, including positive synthetic SHA and negative wrong-size/changed-content/unknown-name/null cases. [Android platform CI41561256441](https://github.com/alwansan/raf/actions/runs/41561256441) **COMPLETED SUCCESS**. No Unity/APK, OBB publication, new LFS transfer, audible device test or gameplay proof. **AUDIO-004 remains SOURCE_FIXES_VALIDATED / runtime acceptance pending.** Maintain NOT_READY: WATER-001 and RENDER-002 remain open. Previous game delivery remains APK80 at9462f8edd8cdb5becbccb96521f2876ef9924410.


<!-- readiness-coordinator-20261103-typedimage-cl -->
## Readiness coordinator live review — 3 November 2026

Current [APK readiness ledger](../docs/APK_BUILD_READINESS.md) has **NOT_READY** with verified WATER-001/RENDER-002 authenticity blockers, unresolved DISPLAY-003/PERF-007 integration reviews, and new FFT-FORMAT-009 (actual compiler-roundtrip image-type mismatch) / HAPTICS-008 (old-device missing-path review). Source [97b242ee](https://github.com/alwansan/raf/commit/97b242ee8a80aa7c5d8a76cf2b3fcbdba4e1031b), [authenticated original FFT CI41561153253](https://github.com/alwansan/raf/actions/runs/41561153253) **SUCCESS**:20/20 original programs kept bindings and workgroups, **0/20** exact typed-image equality; for storage image set0/binding2, original SPIR-V `format_enum=0 (Unknown)`, HLSL recompiled `format_enum=1 (Rgba32f)`. Compiler declaration drift is verified; semantic/Unity image-format equivalence and phone GPU execution are **not**. No water shader/kernel restoration accepted.

Independent [audio commit25624798](https://github.com/alwansan/raf/commit/25624798d1bda6ffcd7ae6e5e8300d59a2819f65) adds SHA/size verification of five original banks *before* Android FMOD load, source [CI41561256404](https://github.com/alwansan/raf/actions/runs/41561256404) and [platform41561256441](https://github.com/alwansan/raf/actions/runs/41561256441) SUCCESS, but Unity integration and audible device result remain pending. Four 2 November [CL LogRaft session folders](https://github.com/alwansan/CL/tree/main/raft%20log/lf) now include [205608](https://github.com/alwansan/CL/blob/main/raft%20log/lf/LogRaft-20261102-205608-054/session-summary.json) with71,670 pass errors,5,941 kernel errors,35 haptics missing paths; this is historical installed-game evidence, not evidence about unbuilt source repairs. A separate [205325](https://github.com/alwansan/CL/blob/main/raft%20log/lf/LogRaft-20261102-205325-994/session-summary.json) signaled PID status9 has unknown cause, not proven OOM/forced stop.

Full delivery workflow and packaging script inspected; strict genuine water compute gate still hard-fails, so **no new candidate / Unity request / APK/OBB/XAPK**. Last complete game remains [APK80/41448086401](https://github.com/alwansan/raf/actions/runs/41448086401), immutable source9462f8ed. Latest readiness documentation [commit 5daa1dd](https://github.com/alwansan/raf/commit/5daa1dd0e67d42ad1a39f3789b994704f8e784bf) records evidence and candidate/build ledger. Continue source repairs without touching any automation or protected branch. Before readiness declaration verify actual shader pass/GUID/kernel/FFT format, local world/.rgd, FMOD, display/input/performance and active runs; phone-only acceptance follows a genuinely produced build.


## Parallel-safe DISPLAY-003 investigation — 3 November 2026

Added SHA-pinned, private original CSharp9 Settings/DynamicResolution lexical reference audit with three local synthetic tests and new lightweight offline integration CI wiring. [Scope, evidence and limits](../docs/ORIGINAL_ANDROID_DISPLAY_AUDIT_2026-11-03.md). Actual original-source counts must be confirmed by the new run; this is not a proven Settings cause or runtime aspect repair. Concurrent FFT typed-image and FMOD work was left untouched. WATER-001/RENDER-002 and DISPLAY-003 remain open; NOT_READY, no Unity/native game build, no request JSON/automation change.


## FFT target format source correlation — 3 November 2026

New SHA-pinned source probe confirms original temporary cache uses RGHalf/RGFloat when two-channel flag is false and ARGBHalf/ARGBFloat when true, selected by precision; dimensions are2N by2N, linear, with original UAV flag forwarded. Local authenticated GpuFFT source passed; two fail-closed synthetic tests passed. Original-source managed CI will verify fresh decompilation; its result is pending. This narrows FFT-FORMAT-009: a fixed Rgba32f compiler declaration cannot be assumed equivalent to all four original requested formats. Actual created graphics format, cache implementation and GPU compatibility remain unverified. No shader, native request, assets or automation changed; NOT_READY retained.


Live validation links for source3da39e4: [CI runner guard41561621224](https://github.com/alwansan/raf/actions/runs/41561621224) COMPLETED SUCCESS; [original private-CSharp offline integration41561621297](https://github.com/alwansan/raf/actions/runs/41561621297) IN_PROGRESS at the last review. These are distinct checks. No final authenticated reference counts or original managed compile result should be claimed until the second run is complete.
