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


### Confirmed original-source result — CI 41561621297, 3 November 2026

[Original private-CSharp integration 41561621297](https://github.com/alwansan/raf/actions/runs/41561621297), job 125673324742, **COMPLETED SUCCESS** for source 3da39e4daa39b150e21a232d78e10d10028c2302. All three new synthetic tests passed on GitHub; both original GraphicsSettingsBox/DynamicResolution SHA256 pins matched; 2,394 original CSharp9 files were examined. Output: zero external **explicit qualified** writes to m_widthScale or m_heightScale, and no explicit DynamicResolution class reference in GraphicsSettingsBox. The declared DynamicResolution class was the only occurrence of its class name in this bounded scanner; two ScalableBufferManager.ResizeBuffers sites remain at original lines 37/55; ApplyCurrentResolutionAndFullscreenMode occurs four times, all within GraphicsSettingsBox (lines 250,255,452,549). Adapted original managed compile exit=0, errorCodes={}. [Runner guard 41561621224](https://github.com/alwansan/raf/actions/runs/41561621224) also SUCCESS. Note: emitted occurrences include declarations and calls; they are NOT a reconstructed control-flow graph. The absence of direct class references/writes does not exclude aliases, reflection, event-driven UI resize, Unity engine-native scale mutation or on-device aspect issues. No Settings cause has yet been identified and no game runtime code was altered. DISPLAY-003 remains SOURCE_REVIEW_REQUIRED; WATER-001/RENDER-002 remain OPEN and build readiness NOT_READY.


## New verified original FFT source-format evidence — 3 November 2026

Concurrent [source81edb578](https://github.com/alwansan/raf/commit/81edb5780d3ef906069822ab6e20e31583fd02bf) confirmed original GpuFFT temporary RenderTexturesCache chooses RGHalf, RGFloat, ARGBHalf or ARGBFloat for 2N×2N linear render targets based on channel count and precision. [Run41561700091](https://github.com/alwansan/raf/actions/runs/41561700091) FAILED due solely to an escaped literal newline merging two shell commands. Repaired workflow in [ee027d9d](https://github.com/alwansan/raf/commit/ee027d9d9f096496d6d15a35008c39714b82fccd) by expected-SHA fast-forward without altering the concurrent original-source probe. [Replacement run41561918626](https://github.com/alwansan/raf/actions/runs/41561918626) COMPLETED SUCCESS, job125674275806, validating the original private source and baseline 194887 FFT numerical checks exit0. This does not prove original Unity cache image format, actual kernels, SPIR-V/HLSL numerical equivalence or phone water rendering; format Unknown→Rgba32f at storage binding2 is not safe to assume equivalent for four original formats. Water gate remains false; readiness NOT_READY, no Unity or native request; all existing tasks unchanged.



## Original FFT cache/format source proof and owner's triple-check gate — 3 November 2026

New [cache scan10d38455](https://github.com/alwansan/raf/commit/10d384554d00affdc170082625a5c692efdd3fd0)/[CI41562582726](https://github.com/alwansan/raf/actions/runs/41562582726), [pinned cache lineage3452a898](https://github.com/alwansan/raf/commit/3452a898f5787e75a75c08b7acff52a851a9ce3e)/[CI41562995693](https://github.com/alwansan/raf/actions/runs/41562995693), and [four-format matrix9d98f43c](https://github.com/alwansan/raf/commit/9d98f43c75eeec1ad75fd0e34625a441a13446c0)/[CI41563298155](https://github.com/alwansan/raf/actions/runs/41563298155) are COMPLETED SUCCESS, CPU-only, no Unity/LFS hydration. Original RenderTexturesCache source SHA 4157076c3e4bddc27ac5b24da768d29ff9e6c227c4da07a9e2f55ae9ff6b8245; five-argument RenderTexture ctor, source-level direct format reference, Linear/sRGB options, one true-literal randomWrite assignment of unknown reachability. Source-requested modes RGHalf/RGFloat/ARGBHalf/ARGBFloat yield expected Vulkan image formats; compiled Rgba32f output only matches expected ARGBFloat, not other three, **conditional on actual image views matching requested formats**. This is not runtime GPU or shader correctness proof. [Full investigation report](../docs/ORIGINAL_FFT_STORAGE_IMAGE_MATRIX_2026-11-03.md).

Owner now requires **three complete independent readiness reviews against the same immutable candidate**, with any candidate input change resetting prior reviews. Updated AGENTS, current owner requirements, copy-ready resume prompt and readiness ledger. Current full reviews **0/3**; outstanding authentic water/source/graphics/other integration blockers mean **NOT_READY**. Do not issue a native request or duplicate scheduled tasks. Continue source/format/2-pass shader/Unity capability investigation and actual repairs; maintain original assets and .meta/GUID/.rgd.


## FFT cache lifetime / memory bounded proof — 3 November 2026

Added [cache-lifetime probe0effd8f1](https://github.com/alwansan/raf/commit/0effd8f1698e1769c055148c8d6ef7b09e874f18), [private original-source CI41563786696](https://github.com/alwansan/raf/actions/runs/41563786696) COMPLETED SUCCESS. RenderTexturesCache original-source lexical counts:1 new RenderTexture,1 Create,2 Release,2 Dispose,2 Destroy,1 Clear,0 Remove. This is evidence of available cleanup APIs, not actual execution or proof of no leak. A single2N×2N target at N512 is4 MiB RGHalf,8 MiB RGFloat,8 MiB ARGBHalf,16 MiB ARGBFloat. Active number/quality/lifetime and actual GPU memory remain unknown; do not equate these amounts with on-phone GPU OOM. [Details](../docs/ORIGINAL_FFT_STORAGE_IMAGE_MATRIX_2026-11-03.md). No game Unity build, no device trial; strict water and triple readiness gates remain blocked, 0/3 and NOT_READY.


## Authentic FFT formatless-write experiment — 3 November 2026

[Original 20-program operation probe 41564682850](https://github.com/alwansan/raf/actions/runs/41564682850) COMPLETED SUCCESS on source 59a4a13b. All twenty SHA-authenticated DXBC programs translated to SPIR-V declare StorageImageWriteWithoutFormat capability 56, contain one OpImageWrite and three OpImageFetch per program, and use an Unknown-format storage image. The HLSL/glslang roundtrip instead declares Rgba32f and removes capability 56, with image-operation counts unchanged. No device feature support or numeric output proven.

[Temporary repair source f2507f00](https://github.com/alwansan/raf/commit/f2507f00bf8e7bcbf5aaf312a7b462b9f82aff31), [original program CI 41565279755](https://github.com/alwansan/raf/actions/runs/41565279755), job 125685201003, COMPLETED SUCCESS: a fail-closed, private-only experiment restores ImageFormat Unknown and OpCapability56 in each translated output, verifying 20/20 original typed-image declarations and 20/20 Vulkan1.1 spirv-val checks. Modified SPIR-V files exist only in private CI temporary directories and were never staged into game assets or published. This is structural restoration, NOT GPU numerical equivalence, original Unity runtime kernel identity, correct game water, or Adreno feature proof.

[Format classification fix 298faf7a](https://github.com/alwansan/raf/commit/298faf7aa6ad7879dbd9cb0a53e411cce0a9bcae) passed [managed source CI 41564904076](https://github.com/alwansan/raf/actions/runs/41564904076). SPIR-V StorageImageExtendedFormats capability is different from Vulkan shaderStorageImageExtendedFormats device feature: RGFloat has Vulkan core-mandatory storage format support, RGHalf may require individual format query when the extended-format guarantee is absent. See [Khronos features specification](https://docs.vulkan.org/spec/latest/chapters/features.html).

NEXT: test genuine numerical FFT GPU/shader outputs and resource-format dependence; correlate runtime kernel mapping and authentic multi-pass ShaderLab programs. Do not fake kernels, toggle strict water gate or claim actual GPU execution. WATER-001, RENDER-002, FFT-FORMAT-009 remain OPEN; readiness NOT_READY, complete immutable candidate audits 0/3, no APK/OBB/XAPK request. No changes to original assets, GUIDs, save content or existing scheduled tasks.


## Authenticated FFT operand dataflow and LFS quota-safe CI — 3 November 2026

[Original 20-program SPIR-V image dataflow source 3207cb41](https://github.com/alwansan/raf/commit/3207cb418e0b73103de56c816eac075c2eedd8f9), [authentic original SHA-checked CI 41565889051](https://github.com/alwansan/raf/actions/runs/41565889051), job125687195811, COMPLETED SUCCESS. The source and HLSL roundtrip each resolve image operation operands without ambiguous/unresolved references for all20 variants: ONE OpImageFetch per program reads set0/binding0; TWO fetches read set0/binding1; ONE OpImageWrite writes set0/binding2. No OpImageRead is used. The result is static SPIR-V operand-to-variable lineage through explicit loads/aliases, not an original Unity runtime kernel lookup, numeric shader equivalence or Android GPU execution. The earlier formatless 20/20 private Vulkan validation remains structural only.

[Source/test/workflow correction 358e42b0](https://github.com/alwansan/raf/commit/358e42b0d2863b53d5904d82ed1209a897d3603a) strengthened the synthetic copy-alias negative control and corrected OpSelect parsing. New [lightweight water/FFT synthetic CI 41566206211](https://github.com/alwansan/raf/actions/runs/41566206211) COMPLETED SUCCESS with no Unity or LFS. The heavy original-resource workflow now triggers from relevant source/probe/workflow changes, NOT synthetic test-only edits; tests still run inside a heavy original-data audit when needed. This avoids 337660952-byte repeat LFS downloads for test-only changes. The corresponding original-LFS workflow [41566206022](https://github.com/alwansan/raf/actions/runs/41566206022) was queued/running at this checkpoint; verify it before recording a real-data result for this later source revision.

WATER-001, RENDER-002 and FFT-FORMAT-009 remain OPEN. Actual shader binding in Unity, image view formats/Adreno features, complete kernel identity, multipass shaders, numeric correctness and all device acceptance remain unverified. Last game test APK80 is older than these source changes. The full build readiness state stays NOT_READY with 0/3 complete reviews on one immutable candidate. No native request, release, original game asset/GUID/save modification or scheduled task mutation.


## Final confirmation — separate synthetic lane and same-source original audit

[Final full LFS audit 41566206022](https://github.com/alwansan/raf/actions/runs/41566206022), job125688252081, COMPLETED SUCCESS on source358e42b0d2863b53d5904d82ed1209a897d3603a after the OpSelect/copy-alias test refinement: all 20 original programs retain uniquely resolved image operation bindings and all20 temporary formatless patched modules pass Vulkan1.1 and match original typed-image declarations. [Independent no-LFS synthetic CI41566206211](https://github.com/alwansan/raf/actions/runs/41566206211) also COMPLETED SUCCESS on the exact same source. Distinguish both source checks from Unity or device operation. The new lean lane permits future synthetic-only edits without triggering another 337660952-byte original LFS hydration.

No source/resource acceptance is upgraded: WATER-001, RENDER-002 and FFT-FORMAT-009 remain OPEN, native test candidate is absent, full readiness audits0/3 and NOT_READY. Latest complete game delivery is still APK80, not these later changes.


## Binary16 FFT coordinate boundary experiment — 3 November 2026

Executed an independent CPU numeric experiment with native IEEE binary16 DataView conversion for every packed half-texel center (i+0.5)/(2N). At N32/64/128/256/512 all centers and floor-based point-sampling indices remain exact. Negative controls N1024 and2048 produce512 and1536 wrong pre-clamp sample indices respectively, with one decoded upper-bound index each. This explains a precision boundary of the modeled lookup representation, not a measured GPU fault or proof of why the original algorithm switches paths. It must not be used to clamp game size, alter quality or claim restored shaders. Hardware clamp/filter/format behavior and actual translated shader numerical output remain unverified. Reproducible experiment: scripts/audit_fft_binary16_addresses.mjs (requires native DataView float16 support). The core function was executed in the tool JS runtime; no Node/GitHub CI execution is claimed. No Unity/native request, LFS or automation change. NOT_READY and readiness0/3 remain unchanged.


## Readiness recheck — 3 November 2026, 07:47 Baghdad

Live branch review at 5368aef31ce07e982805c63056713b694e0e6cda: no queued/in-progress Actions returned. Latest binary16 address experiment remains CPU/model-only; it does not close WATER-001, RENDER-002 or FFT-FORMAT-009, and does not count as any of the three complete immutable-candidate reviews. No candidate selected, readiness0/3, NOT_READY. No native request or build started. Next evidence remains actual translated FFT numerical/format behavior and authentic complete shader restoration, plus the unresolved integration reviews already listed. Existing task configurations and native request files remain unchanged.


## Readiness evidence refresh — 3 November 2026, 08:31 Baghdad

Reviewed HEAD 415e51b082bb2c1fff4d7c5d1518205d89d4af91 and nonterminal Actions (none queued/in_progress returned). Existing WATER-001/RENDER-002/FFT-FORMAT-009 source blockers and incomplete integration reviews remain unresolved; no immutable ready candidate exists and complete reviews remain0/3. The latest CPU coordinate experiment is not a substitute for translated-program numerical or Unity image-format evidence. NOT_READY retained; no native request or retry issued. Last game release remains APK80/source9462f8e,11 delivery assets; current CL root identities match the prior review. Next action remains source/resource closure, not a repeated native build.


## Reproducible FFT coordinate test lane — 3 November 2026

Executed scripts/audit_fft_binary16_addresses.mjs under actual Node24.22.1 locally: all7 size rows and built-in compute-range/negative-boundary assertions passed (exit0), matching the earlier tool-JS experiment. Added an isolated5-minute CPU-only Node24 Actions lane, triggered only by the address script or its own workflow; no Unity, LFS or shared heavy compute audit is started. Remote result pending; this improves reproducibility rather than proving shader/GPU behavior. No shader or original game input changed, and NOT_READY/0-of-3 remain unchanged.


## Coordinate CI confirmed; readiness unchanged — 3 November 2026

[FFT coordinate precision CI41584946408](https://github.com/alwansan/raf/actions/runs/41584946408) COMPLETED SUCCESS on de5dec1e7aede04c678e68fe62d1933f6a5260ca, confirming the isolated Node24 CPU experiment now runs in Actions without LFS. This supersedes its pending status. It does not validate translated shader output, image-format equivalence, complete water kernels or device operation. WATER-001/RENDER-002/FFT-FORMAT-009 remain open; candidate absent, reviews0/3, NOT_READY. No native request or build initiated.


## FFT half-address Clamp/bank experiment — 3 November 2026

Extended scripts/audit_fft_binary16_addresses.mjs and executed the actual file using Node24.22.1 (exit0). In the authored nearest-point Clamp CPU model, N32–512 retain exact centers and indices; N1024 has511 wrong indices after Clamp,0 cross-half reads; N2048 has1535 wrong indices after Clamp,1 cross-half read. Clamp removes exactly the single outer-edge out-of-bounds address in each larger-size negative control. Exact count assertions prevent treating Clamp as a general precision repair. The initial proposed N1024 cross-half expectation was rejected by execution and corrected to0 before committing. No original shader/quality/format changed. This is a binary16 coordinate model, not hardware filtering, translated-shader numerical equivalence or phone evidence; WATER-001/RENDER-002/FFT-FORMAT-009 stay open, NOT_READY/0-of-3. Existing cheap coordinate CI will validate this source; result pending. Live Actions showed only completed successes; CL directory identities unchanged. No native request, build, release or task changes.


## FFT address precision control — 3 November 2026

Confirmed [Clamp/bank CI41591309793](https://github.com/alwansan/raf/actions/runs/41591309793) COMPLETED SUCCESS. Added an independent binary32 address control to the same CPU experiment and executed the changed file with Node24.22.1, exit0: all8128 packed-center indices across N32–2048 remain correct using Math.fround, while the binary16 negative controls retain511/1535 post-Clamp errors at N1024/2048. This isolates storage precision as the cause within this model; it does not prescribe changing original texture formats or establish shader/GPU behavior. New-source CI pending. Live Actions contained no active run in the latest four; CL root identities unchanged; newest release lograf-63 is a logger release, not a new game APK. WATER-001/RENDER-002/FFT-FORMAT-009 remain open; NOT_READY/0-of-3. No Unity/LFS/native request/task changes.


## Candidate evidence refresh — 3 November 2026, 11:04 Baghdad

Live source baseline 83bb6497f5772965521f57bb9b440fac789c0430. [Float32/half coordinate CI41598252205](https://github.com/alwansan/raf/actions/runs/41598252205) COMPLETED SUCCESS; this supersedes the pending coordinate-control result. The comparison validates the authored CPU address model only, not translated FFT numerical equivalence or original shader restoration. WATER-001, RENDER-002 and FFT-FORMAT-009 remain OPEN, and the DISPLAY-003/PERF-007/integration source reviews are incomplete. No candidate selected; complete immutable-candidate reviews0/3; NOT_READY. Explicit repository-wide queued and in_progress queries both returned empty. APK80 release still has11 assets; CL raft-log root identities unchanged. No new build attempt/error/request or recovery artifact exists for a candidate. Next: close authentic program/pass/kernel and format/numerical contracts, then complete the listed integration reviews; phone-only acceptance remains post-delivery. No native request or task changes.


## SPIR-V partial-unknown union repair — 3 November 2026

Fixed a demonstrated false-positive in image-slot lineage: an OpSelect with one known descriptor and one unknown resource previously discarded the unknown branch and claimed a unique binding. Unknown ancestry now propagates explicitly and marks the operation unresolved. Added a synthetic regression; all6 image-flow tests passed locally with Python unittest. This repairs audit trust, not original shader behavior; prior direct-load results are not evidence for mixed dynamic branches. Original-program audit must be rechecked on the new source; no GPU/Unity equivalence claimed. WATER-001/RENDER-002/FFT-FORMAT-009 remain open, NOT_READY/0-of-3. No native request or task modification.


## Corrected lineage audit confirmed — 3 November 2026, 11:57 Baghdad

On source de4eb605a20f61878f5a48cb917f3642e447cfd2, [synthetic CI41605046080](https://github.com/alwansan/raf/actions/runs/41605046080) and [authenticated original-compute audit41605045982](https://github.com/alwansan/raf/actions/runs/41605045982) both COMPLETED SUCCESS. Read job125812668548 actual logs:20 translations validate for Vulkan1.1,20 binding/workgroup comparisons pass, but typed-image preservation remains0/20 and image-operation/capability profile preservation0/20. Thus the partial-unknown fix does not erase the independently observed format/capability discrepancy. WATER-001/RENDER-002/FFT-FORMAT-009 stay OPEN; full integration source reviews remain incomplete. Candidate absent, reviews0/3, NOT_READY. All five nonterminal status queries (queued/in_progress/waiting/pending/requested) returned empty. CL root identities unchanged; APK80 release still11 assets. No build request, attempt, new build error or candidate recovery artifact. Next evidence is actual translated numerical/format reconciliation and authentic full shader restoration; phone-only tests remain post-build.
