# T1 — direct original-SPIR-V FFT invocation-keyed ImageFetch recorder

- session_id: 20261106T161112Z-T1-chat-original-keyed-recorder-7be2
- origin: chat
- status: completed (authentic original direct SPIR-V keyed GPU readback)
- issue_id: WATER-001 OPEN / NOT_READY
- base_sha: f70eb499f157c5af40ff2c74712d1e039cc0d79b
- resumed_from_sessions: 20261106T155244Z-T1-chat-original-builtin-inject-d5f2; 20261106T153545Z-T1-chat-original-actual-preflight-d8e2; 20261106T151730Z-T1-chat-keyed-candidate-3a7f
- scope_commit: cb61bfe59f5f8d5c2667e6005ce4a88c33e45fe1
- original_source_sha: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- instrumenter_commit: a89cdcd0a915189bb4de52f8390f94432a950d27
- instrumenter_tests_commit: 5162be8ec6af27c035cabdb2d3bdd687f6cfccc3
- source_only_workflow_commit: 28e00702ebf48a5de435477f0e6c2beba5c80cc0
- original_runner_source_commit: df32d5df80b93ebcf64ebffc3f4304ac6006714a
- private_vulkan_workflow_commit: 5f14e39df64c57a17ed820afc2fa8a94dd4dfae4
- source_only_run: https://github.com/alwansan/raf/actions/runs/42250625172
- actual_original_run: https://github.com/alwansan/raf/actions/runs/42250952529
- work: prompt/coordination/work/WATER-001/T1-20261106T161112Z-T1-chat-original-keyed-recorder-7be2.json
- experiment_key: water001-sourcepin15964ea8-original-spirv-3imagefetch-direct-signed3-gid-ssbo-keyed-capture-v1

## Source-authentic reason for new experiment

Private original FFT SPIR-V SHA-pin and explicit 3 fetch roles verified in 42244565958, original GlobalInvocationId formerly reported `not_proven`. Latest actual private CI 42249043033 proved one existing `GlobalInvocationId` direct `Input` **signed int3** member, present in compute entry interface with two direct `OpLoad` uses. Therefore adding another BuiltIn is invalid (safely rejected in 42248163030). The HLSL-roundtrip candidate already produced 384 real invocation-keyed reads [64, 256, 64] via 42242127723, but original independently keyed reads and real numerical parity were still missing.

## Code and bounded safety

New `scripts/t1_fft_original_direct_keyed_recorder.py` edits a **private staging-only** original SPIR-V assembly copy without traversing HLSL. It keeps three unchanged `OpImageFetch` instructions and appends per-site 12-u32-word keyed records at descriptor set0/binding3, with signed3 builtin bit reinterpretation **only for output keys**, unsigned atomic record index, 512 record capacity clamped on overflow with a detectable total counter, independent per-site per-invocation occurrence counters, original sint2 fetch coordinate bits and original float4 fetched value bits. It refuses existing reserved namespace, descriptor binding collision, wrong fetch role/shape, missing signed3 input, nonentrypoint fetch, and unsupported module shape; no source token/SSA IDs, image bytes, raw shader or pixel values are logged.

New `tests/test_t1_fft_original_direct_keyed_recorder.py` 15 synthetic tests. [Source-only CI 42250625172](https://github.com/alwansan/raf/actions/runs/42250625172) SUCCESS (111 previous + 15 recorder cases = **126 tests**), no original private shader loaded in this test.

New `scripts/t1_fft_original_trace_vulkan.py` stages original ZIP2 slot0 private shader, disassembles, instruments the original directly, assembles with `spirv-as --target-env vulkan1.1`, validates with `spirv-val`, and runs the existing proven Vulkan host with trace buffer bound to **set0** (original pipeline). The shader output is checked against the unmodified original on the same Vulkan input/dispatch. It refuses duplicate, incomplete or overcapacity records; expected per-site counts [64, 256, 64]. Trace bytes stay in private runner scratch, never Artifacts, and are deleted on job cleanup. Previous HLSL candidate trace uses set1, so this is independent original capture, not a self-comparison.

## Live CI checkpoint

[GitHub Actions 42250952529](https://github.com/alwansan/raf/actions/runs/42250952529) started @`5f14e39`, status in_progress at checkpoint. Inspect actual source-authentic `RAFT_T1_ORIGINAL_KEYED_INSTRUMENT` and `RAFT_T1_ORIGINAL_SPIRV_KEYED_GPU_TRACE` markers only after runtime/spirv-val passed. If private source architecture differs (functions, pointer/addressing or SPIR-V validator), treat it as an engineering blocker, log a safe failure category, and repair only after evidence; no partial success claim. Do not cancel others or launch a duplicate private Vulkan runner.

## Handoff

After successful original trace: capture candidate HLSL on **byte-identical source/butterfly input and dispatch** within one attested runner, compare two independent trace buffers using `scripts/t1_fft_invocation_pair_gate.py` and ULP helper. Even separate captures alone do not prove equal values. No authored Unity shader, native Android APK, settings/audio, or other T-team input files changed. WATER-001 OPEN; Android water/Adreno acceptance unproven.

## Actual original-SPIR-V GPU result — completed

- Initial run [42250952529](https://github.com/alwansan/raf/actions/runs/42250952529) failed in new private original recorder without a stage category. Added fixed safe stage markers, reran [42251375883](https://github.com/alwansan/raf/actions/runs/42251375883): original disassembly + source-only instrumentation + `spirv-as` **passed**, `spirv-val` failed. Only safe validator categories were exported in [42251789167](https://github.com/alwansan/raf/actions/runs/42251789167): `OpEntryPoint`, `OpVariable`, `StorageBuffer`.
- Confirmed the exact rule with the Khronos SPIR-V specification: **SPIR-V 1.3 and earlier `OpEntryPoint` interface IDs are limited to Input/Output storage classes**; the new `StorageBuffer` global must be declared/bound but not listed in `OpEntryPoint` on `--target-env vulkan1.1`. Corrected only this section, preserving all original signed-int3 BuiltIn GID, original ImageFetch instructions and keyed record stores. Test suite added explicit negative regression for this rule.
- Corrected source-free [42252142102](https://github.com/alwansan/raf/actions/runs/42252142102) **SUCCESS, 127/127 Python tests**, including 16 source-only SPIR-V original keyed recorder cases.
- Actual SHA-pinned original GPU [42252268973](https://github.com/alwansan/raf/actions/runs/42252268973) job `128010174020`, source workflow commit `e9ef2627d8bc09e007c5d2d59da1385136e5778b`: **SUCCESS** with original ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` recovered/verified, private original `slot0.spv` disassembled, instrumented **directly without HLSL conversion**, reassembled `spirv-as`, validated `spirv-val`, compiled original-pipeline trace C++ host, Vulkan dispatched/read back, and all private scratch deleted.
- Exact safe marker: `RAFT_T1_ORIGINAL_SPIRV_KEYED_GPU_TRACE` record count **384**, source / butterfly1 / butterfly2 **[64, 256, 64]**, **0 duplicate** dispatch+occurrence keys, 512-capacity buffer not overflowed. Original traced shader vs **unmodified original shader** outputs invariant across **64 actually written pass-zero pixels** in same-input Vulkan execution. Original signed FFT coordinate arithmetic remains unchanged, only new record storage uses bitwise unsigned-key representation. No original bytecode, SHA source, private pixel, image or trace buffers published.
- HLSL-roundtrip keyed candidate [42242127723](https://github.com/alwansan/raf/actions/runs/42242127723) also produced **384** records [64,256,64] independently. **No original-vs-HLSL per-invocation pairing was performed**. Equal counts are not numeric parity. Production authored Unity shader binding, android GPU/Adreno and WATER-001 remain OPEN/NOT_READY.

## Completed scoped handoff

- status: completed / resource released
- experiment: `prompt/coordination/experiments/T1/20261106T161112Z-T1-chat-original-keyed-recorder-7be2.json`
- canonical event: `prompt/coordination/B_TEAM/events/T1/20261106T161112Z-T1-chat-original-keyed-recorder-7be2.json`
- next_step: new independent T1 scope to capture original and HLSL in a single SHA-pinned private fixture, **hash-compare actual source/butterfly input readback bytes and dispatch configuration inside runner**, then feed two distinct keyed binaries to `scripts/t1_fft_invocation_pair_gate.py` with bound manifest to report per-site coordinate/value disagreement. Keep all original source/trace private and do not claim original-vs-candidate numeric equivalence based on aggregate counts, static SPIR-V structure or one shader's output invariance. Only after genuine per-invocation first divergence should HLSL be modified for correctness and device tested.
