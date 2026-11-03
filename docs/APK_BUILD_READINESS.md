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

| FFT-FORMAT-009 | OPEN — typed-image roundtrip discrepancy, cause to reconcile | [CI 41561153253](https://github.com/alwansan/raf/actions/runs/41561153253) SUCCESS on source 97b242ee: authentic 20 original FFT DXBC programs translated and validated; 20/20 workgroup and binding contracts preserved, **0/20** exact typed-image declarations. The exact observed difference in first program is set0/binding2 `format_enum` original **0 (Unknown)** versus recompiled **1 (Rgba32f)**; no bound-slot loss. Not proof of Android GPU malfunction or numerically unequal compute. | Determine if glslang's explicit storage-image format is valid/semantically equivalent under the original usage and actual Unity RenderTexture data formats; compare all20 numeric differences and FFT output with a suitable test, preserve GPU behavior, never assert source authenticity from compilation alone. |
| HAPTICS-008 | SOURCE_REVIEW_REQUIRED — impact unknown | [CL LogRaft 205608 session](https://github.com/alwansan/CL/blob/main/raft%20log/lf/LogRaft-20261102-205608-054/session-summary.json) documents35 haptics asset path lookup errors on previously installed game, and CL has four dated 2 November session folders. Neither current source resource absence nor mandatory startup impact proven. | Extract exact missing asset path from relevant raw game log, trace current resource GUID/build staging and classify mandatory vs optional. Do not block on device vibration-only proof. |

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


## Confirmed original FFT image-format roundtrip drift — 3 November 2026

[First authenticated audit41560719688](https://github.com/alwansan/raf/actions/runs/41560719688), source c1ba4a74, completed SUCCESS. All20 original sha-authenticated FFT-name DXBC programs produced20/20 validated SPIR-V and20/20 HLSL/glslang roundtrips. There are60 original image-variable declarations: per program set0/binding0 and binding1 are sampled float32 2D images (sampled_enum1), set0/binding2 is a storage float32 2D image (sampled_enum2); all three declare format_enum0 (Unknown). The complete typed declarations matched only0/20 after roundtrip even though workgroups and descriptor slot numbers matched20/20.

[Exact drift-diagnostic commit97b242ee](https://github.com/alwansan/raf/commit/97b242ee8a80aa7c5d8a76cf2b3fcbdba4e1031b) plus [authenticated audit41561153253](https://github.com/alwansan/raf/actions/runs/41561153253), job125671805049, completed SUCCESS. All20 programs have the SAME and ONLY declared type difference: storage output set0/binding2 format_enum0 (Unknown) becomes format_enum1 (Rgba32f) on SPIRV-Cross HLSL50 → glslang SPIR-V. Other listed scalar/width/dim/sampling/access declarations and resource slots remain identical. This is a representation change, not proof of wrong rendered pixels or numerical equivalence. Establish original Unity output RenderTexture format, ShaderLab bindings, supported Vulkan formats and numerical output before choosing a faithful restoration; never silently treat Unknown as Rgba32f for all phone textures. WATER-001 and RENDER-002 remain OPEN and state NOT_READY. No APK request/build.


### AUDIO-004 authenticated-runtime-bank checkpoint — 3 November 2026

[Source25624798](https://github.com/alwansan/raf/commit/25624798d1bda6ffcd7ae6e5e8300d59a2819f65) checks all five independently authenticated original bank byte lengths and SHA-256 values immediately before FMOD receives loaded APK/OBB data. Audio C# [41561256404](https://github.com/alwansan/raf/actions/runs/41561256404) SUCCESS (53 executable policy checks); platform [41561256441](https://github.com/alwansan/raf/actions/runs/41561256441) SUCCESS. No source asset changed or LFS download, Unity/native build or on-device sound test. AUDIO-004 remains SOURCE_FIXES_VALIDATED / integration and device acceptance pending. This source-only addition does not close WATER-001 or RENDER-002 or select a candidate SHA; readiness remains NOT_READY.


<!-- coordinator-audit-20261103-typed-image-cl -->
## Readiness coordinator audit — 3 November 2026, live-source and CL evidence

**Decision: NOT_READY**; no candidate_source_sha, new request_id, native run_id or new signed output. Reviewed live HEAD `25624798d1bda6ffcd7ae6e5e8300d59a2819f65` before this docs-only update. Independent concurrent source commits include `c1ba4a74` and `97b242ee` for authentic FFT SPIR-V image declarations and `25624798` for original FMOD bank byte verification; do not override their edits. Their [compute CI 41560719688](https://github.com/alwansan/raf/actions/runs/41560719688) and [refined compute CI 41561153253](https://github.com/alwansan/raf/actions/runs/41561153253) completed SUCCESS, but neither executes Android GPU, complete water rendering, Unity, or device gameplay.

**WATER-001 / RENDER-002 still OPEN.** Actual [native workflow](../.github/workflows/raft-unity-editor-android-import.yml) calls [`scripts.verify_water_render_contract --strict`](../scripts/verify_water_render_contract.py) before Unity import; its `authentic_water_kernel_identity_verified` remains false with intentional fail-closed gate. Authentic ShaderLab passes, compute kernel identities and selectors, original .meta/GUID materials and both FFT passes, butterfly numeric/texture/stage behavior and actual source staging still need provenance-linked source checks. Do not toggle this flag without authenticated restoration. New **FFT-FORMAT-009**: `41561153253` confirms 20/20 descriptor bindings/workgroups, 0/20 exact image-type roundtrip, specifically original storage output slot `set0/binding2 format_enum=0 (Unknown)` became `format_enum=1 (Rgba32f)` in recompiled SPIR-V on first program. This is a *compiler declaration difference*; its semantic/Unity format impact is **UNKNOWN**, not an established GPU failure. Continue discriminating typed-image/layout and per-stage numeric checks.

**CL evidence and new HAPTICS-008.** Inspected four 2 November `alwansan/CL/raft log/lf` sessions; last [205608-054](https://github.com/alwansan/CL/blob/main/raft%20log/lf/LogRaft-20261102-205608-054/session-summary.json) records **71,670** invalid shader passes (44,578 UltimateWater,17,824 bilateral blur,9,268 others), **5,941** invalid compute kernels, **35** haptics path lookup errors. These are counts from an installed older game, **not** a new-source CI/device test, and the exact APK source SHA is not attested in the collector summary. [205325-994](https://github.com/alwansan/CL/blob/main/raft%20log/lf/LogRaft-20261102-205325-994/session-summary.json) shows pid20115 `SIGNALED` status9 with **cause unproven**; separate older pid4494 explicitly `USER REQUESTED/FORCE STOP`. Do not assert OOM/manual stop. 205608 process RSS peak2,214,412KiB, external KGSL GPU busy19.23–67.63%, seven readable SurfaceFlinger FPS windows17.74–120.71: **not Unity FPS**. PERF-007 and DISPLAY-003 integration/source review remain open.

**Audio/source delta:** New [FMOD commit 25624798](https://github.com/alwansan/raf/commit/25624798d1bda6ffcd7ae6e5e8300d59a2819f65) adds actual bank length/SHA256 verification in Android OBB load path before `loadBankMemory`. [Audio CI 41561256404](https://github.com/alwansan/raf/actions/runs/41561256404) and [platform CI 41561256441](https://github.com/alwansan/raf/actions/runs/41561256441) completed SUCCESS. This closes the specific *unverified bank byte input* defect at source/harness level, **not AUDIO-004 overall**: candidate staging/Unity integration and audible device result remain pending. LOCAL-005: validate actual offline world initialize/create/load/save .rgd without fake success. INPUT-006: retain LEFT MouseButton.Left/Mouse0 short click and500ms hold/drag, touch-to-mouse false, UGUI/Xbox/editor/physical peripherals. DISPLAY-003/PERF-007 require current Settings/aspect and resource/memory review before readiness; physical performance, audible FMOD, world, saving, touch and OBB mount then require new phone testing **after** a build, not before.

**Latest reviewed delivery mechanics:** [workflow](../.github/workflows/raft-unity-editor-android-import.yml) uses Unity2021.3.45f2 ARM64 IL2CPP split/fidelity; `raft-android-signed-output-checkpoint` before packaging, `raft-android-audited-output-recovery` on packaging failure, real signature/FMОD/scene/data gates, `package_android_delivery` and lossless SHA256 part/reassembly plus XAPK manifest/OBB/versionCode/package, Release asset names/sizes and final `delivery-result`. [Package code](../scripts/package_android_delivery.py) and [package fixtures](../tests/test_android_delivery_package.py) inspected, but they are not a new signed game audit. Last valid complete game is [APK80 run41448086401/attempt1](https://github.com/alwansan/raf/actions/runs/41448086401), older immutable source `9462f8edd8cdb5becbccb96521f2876ef9924410`, [11 release assets](https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1). Older [run41419971187/attempt1](https://github.com/alwansan/raf/actions/runs/41419971187) failed at **Package complete owner-authorized APK OBB and XAPK delivery** (`PermissionError`), later recovered by complete APK80 run, not a new candidate failure. At branch status check queued/pending/waiting/in_progress were all zero; must recheck each cycle. No equivalent Unity run is being cancelled or repeated. Prior lightweight source/package fixtures:25 passed,1 skipped; **no new Unity/native build or phone trial** in this audit.

**Next step:** Reconcile original storage image format versus HLSL roundtrip numeric declaration and actual Unity format, restore genuine shaders/FFT passes/kernels/.meta/GUID, classify exact haptics lookup, complete DISPLAY/PERF and local save/scene/FMОD/input integration source reviews, run candidate-specific tests, then recheck HEAD/Actions. Only after blockers are truly closed mark READY_FOR_BUILD and send one existing-protocol native request, later verify signed APK+OBB+XAPK full delivery. Do not rebuild merely because the scheduled task repeats.


## Verified original FFT target formats and CI fix — 3 November 2026

Concurrent source [81edb578](https://github.com/alwansan/raf/commit/81edb5780d3ef906069822ab6e20e31583fd02bf) added an original GpuFFT SHA-pinned target-format probe. It proves four source-requested temporary cache formats, chosen by two-channel and precision flags: RGHalf, RGFloat, ARGBHalf and ARGBFloat; dimensions 2N×2N, linear, original random-write flag forwarded. This is source behavior, not a measured instantiated RenderTexture format.

First private managed FFT [41561700091](https://github.com/alwansan/raf/actions/runs/41561700091) failed only because a literal backslash-n joined two Python workflow commands. Corrected the YAML command boundary in [ee027d9d](https://github.com/alwansan/raf/commit/ee027d9d9f096496d6d15a35008c39714b82fccd) via expected HEAD without force. [Follow-up41561918626](https://github.com/alwansan/raf/actions/runs/41561918626), job125674275806, COMPLETED SUCCESS: exact original CSharp9 source format checks and 194887 baseline butterfly numeric checks (exit0), no Unity or game build.

Original SPIR-V output image format Unknown becomes Rgba32f after HLSL roundtrip; actual cache image format, kernel mapping, GPU arithmetic and format support remain unproven. FFT-FORMAT-009/WATER-001/RENDER-002 remain OPEN, NOT_READY. No request, no tasks changed.


## Mandatory 3/3 full independent readiness audits — new owner direction, 3 November 2026

Do not label or document READY_FOR_BUILD until every demonstrated source/resource pre-build blocker is actually closed and **three distinct comprehensive reviews** have independently PASSED for the **same immutable candidate_source_sha**. Re-audit everything each time: live HEAD/concurrent Actions and equivalence, provenance/LFS SHA/.meta/GUIDs/content, authentic UltimateWater/FFT kernel+pass+format behavior and other shader/material programs, FMOD/OBB bank integrity, local create/load/host/.rgd preservation, LEFT Mouse0 short-click/500ms hold and virtual Xbox/physical devices, orientation/Settings/aspect, realistic memory/performance integration, CI tests, Unity2021.3.45f2 workflow, signature/release, genuine APK+OBB+XAPK and signed-output checkpoint/recovery. Record exact commit, evidence links, unresolved issues, reviewer method and completion time for each pass; never count one CI result three times. Any candidate source/resource change invalidates all prior audits (reset 0/3); doc-only change must be proven not to alter candidate inputs. Distinguish pending device-only verification from pre-build blockers so the first device-test build is not blocked by its own future acceptance.

- Review 1/3: NOT STARTED — no complete immutable candidate.
- Review 2/3: NOT STARTED — no complete immutable candidate.
- Review 3/3: NOT STARTED — no complete immutable candidate.

**State remains NOT_READY**. No workflow dispatch or native request from this policy. Existing scheduled tasks unchanged.



## Verified original source cache and typed format matrix — 3 November 2026

[Detailed source and CI proof](ORIGINAL_FFT_STORAGE_IMAGE_MATRIX_2026-11-03.md): [cache audit41562582726](https://github.com/alwansan/raf/actions/runs/41562582726), [pinned format lineage41562995693](https://github.com/alwansan/raf/actions/runs/41562995693), and [four-mode compatibility CI41563298155](https://github.com/alwansan/raf/actions/runs/41563298155) all COMPLETED SUCCESS. Original CSharp9 RenderTexturesCache has one five-argument RenderTexture constructor, and a direct lexical RenderTextureFormat reference as fourth argument. GpuFFT requests RGHalf, RGFloat, ARGBHalf and ARGBFloat by channel/precision. Independently authenticated roundtrip storage output format Rgba32f can exactly match only the expected ARGBFloat view among these four; actual Unity Vulkan image view/device support remains unknown, so this is a FORMAT-CONTRACT RISK not proven visual failure. WATER-001/FFT-FORMAT-009/RENDER-002 remain OPEN. Complete three-pass readiness reviews: **0/3**. NOT_READY; no immutable build candidate selected.


## PERF-007 bounded cache lifetime audit — 3 November 2026

[Original-source CI41563786696](https://github.com/alwansan/raf/actions/runs/41563786696) SUCCESS: original RenderTexturesCache has 2 lexical Release,2 Dispose,2 Destroy,1 Clear and1 RenderTexture creation calls, pinned to the authenticated source SHA. [Full evidence](ORIGINAL_FFT_STORAGE_IMAGE_MATRIX_2026-11-03.md). There is no source-based justification to assert no cleanup APIs. One N512 image is estimated at4 MiB RGHalf,8 MiB RGFloat,8 MiB ARGBHalf or16 MiB ARGBFloat; actual live target counts, GPU alignment and allocator/lifetime reachability are untested. No cause assigned to historical GPU OOM. PERF-007 remains SOURCE_REVIEW_REQUIRED. All source/graphics blockers remain OPEN, no candidate, 0/3 full candidate reviews and NOT_READY.


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


## Readiness recheck — 3 November 2026, 07:47 Baghdad

Live branch review at 5368aef31ce07e982805c63056713b694e0e6cda: no queued/in-progress Actions returned. Latest binary16 address experiment remains CPU/model-only; it does not close WATER-001, RENDER-002 or FFT-FORMAT-009, and does not count as any of the three complete immutable-candidate reviews. No candidate selected, readiness0/3, NOT_READY. No native request or build started. Next evidence remains actual translated FFT numerical/format behavior and authentic complete shader restoration, plus the unresolved integration reviews already listed. Existing task configurations and native request files remain unchanged.
