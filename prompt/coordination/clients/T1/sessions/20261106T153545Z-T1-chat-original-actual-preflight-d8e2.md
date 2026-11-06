# T1 — actual SHA-original FFT SPIR-V keyed capture feasibility

- session_id: 20261106T153545Z-T1-chat-original-actual-preflight-d8e2
- origin: chat
- status: completed (source-authentic original SPIR-V prerequisite diagnosis)
- issue_id: WATER-001 (OPEN / NOT_READY)
- resumed_from_sessions: 20261106T152810Z-T1-chat-original-key-preflight-c41b; 20261106T151730Z-T1-chat-keyed-candidate-3a7f; 20261106T133640Z-T1-chat-nested-phi-8d31
- base_sha: 876ecbfb81206d659e109d6a6dad19cbf8f912dc
- work: prompt/coordination/work/WATER-001/T1-20261106T153545Z-T1-chat-original-actual-preflight-d8e2.json
- scope_commit: 3b029b752ba0706a9e829ab5d5ea26684595de3c
- exact_original_workflow_commit: 315780d1bfd9da3f6ca0cec6fde4a217d67de6d9
- original_source_pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- run_url: https://github.com/alwansan/raf/actions/runs/42244565958
- experiment_key: water001-originalsha15964ea8-real-spirv-slot0-imagefetch-globalinvocationid-free-binding-keyed-read-tracer-prerequisites-v1

## Authenticated starting point / actual engineering

CI [42242127723](https://github.com/alwansan/raf/actions/runs/42242127723) completed SUCCESS with **384 real invocation-keyed reads** from the original-derived *translated HLSL candidate* under same-host Vulkan: source64 / butterfly1 256 / butterfly2 64; 0 out-of-bounds and no duplicate (dispatch, occurrence) keys. This is not an original SPIR-V keyed capture. Source-only [42243693907](https://github.com/alwansan/raf/actions/runs/42243693907) passed 86/86 tests including 12 new original keyed preflight synthetic cases (entrypoint GlobalInvocationId direct or Input struct, ImageFetch signed/unsigned vector coords, result widths, descriptor set0/1 binding3 collisions). No original shader assets are released.

This new distinct source-private scope registered on HEAD after checking no active/queued T1 original Vulkan workflow. Added only one safe call to `scripts.t1_fft_original_keyed_preflight` immediately after pinned original FFT extraction/inventory and before candidate roundtrip, within existing 20min isolated T1 workflow. It should inspect the *real* private original FFT `slot0.spv` and output allowlisted JSON `RAFT_T1_ORIGINAL_KEYED_PREFLIGHT` including roles, vector numeric kinds/widths, `GlobalInvocationId` presence and whether descriptor set 0 or 1 binding 3 is unoccupied. Does not change SPIR-V binary, shader code, kernel mapping, native APK, assets, audio/Settings, deferred touch or other T clients' files. No duplicate T1 runner is scheduled.

## CI pending / exact acceptance

[Run 42244565958](https://github.com/alwansan/raf/actions/runs/42244565958) in progress. Only accept final evidence if exact ZIP2 SHA staging and source-private preflight command completed. If the private original SPIR-V lacks builtin, another source path must be proven; if binding3 occupied, do not invent free binding without checking host descriptor layout. In all cases a source-only prerequisites report is *not* a successful direct original SPIR-V GPU instrumentation or independent paired numeric capture.

After CI terminates, record actual sanitized marker or safe failure in this session, experiment, canonical event and work JSON. The strict `scripts/t1_fft_invocation_pair_gate.py` can be applied only with two independently produced same-input/dispatch keyed GPU capture blobs and attested manifest. No numeric FFT parity/Adreno water claimed; WATER-001 stays OPEN. If private job remains long, keep work waiting_ci rather than cancel or run equivalent overlapping experiments.

## Verified source-private result — final

[GitHub Actions 42244565958](https://github.com/alwansan/raf/actions/runs/42244565958), job `127983274940`, **SUCCESS**. Exact ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` staged, original slot0 private SPIR-V audited, all existing Vulkan/roundtrip stages passed and private scratch cleaned.

Safe `RAFT_T1_ORIGINAL_KEYED_PREFLIGHT` actual result:
- Three original `OpImageFetch` sites: source / butterfly1 / butterfly2.
- Each coordinate = **sint32 vector width 2**; each fetched result = **float32 vector width 4**.
- Descriptor set 0, binding 3 **available**; descriptor set 1, binding 3 **available**.
- Direct or Input-struct-member `GlobalInvocationId`: **not_proven**, therefore cannot assume a ready dispatch-ID variable in the original private SPIR-V.
- `direct_original_spirv_instrumented=false`; `original_invocation_capture_proven=false`; `paired_numeric_parity_proven=false`. No original GPU invocation records actually captured.

The candidate stage was separately verified at [CI 42242127723](https://github.com/alwansan/raf/actions/runs/42242127723), 384 real keyed HLSL candidate reads by site [64,256,64] with no out-of-bounds; it does **not** substitute for an original SPIR-V capture. This experiment only unlocks knowing the original fetch/result numeric type and free descriptor binding. It confirms a genuine input-builtin evidence gap.

## Completed independent handoff

- status: completed, resource released, WATER-001 OPEN / NOT_READY
- experiment: `prompt/coordination/experiments/T1/20261106T153545Z-T1-chat-original-actual-preflight-d8e2.json`
- canonical event: `prompt/coordination/B_TEAM/events/T1/20261106T153545Z-T1-chat-original-actual-preflight-d8e2.json`
- next_step: In a **new** source-private scope, classify any original builtins `LocalInvocationId`, `LocalInvocationIndex`, `WorkgroupId`, `NumWorkgroups` or a safe non-exporting route to inject new `GlobalInvocationId` into SPIR-V. Then validate direct original keyed instrumentation and same-input/dispatch paired original/candidate GPU readback. Do not relabel HLSL translation as original, and do not edit authored game shader based on this preflight.
