# T1 — inject original FFT SPIR-V GlobalInvocationId into private test copy

- session_id: 20261106T155244Z-T1-chat-original-builtin-inject-d5f2
- origin: chat
- issue_id: WATER-001 (OPEN / NOT_READY)
- status: waiting_ci
- resumed_from_sessions: 20261106T153545Z-T1-chat-original-actual-preflight-d8e2; 20261106T151730Z-T1-chat-keyed-candidate-3a7f; 20261106T133640Z-T1-chat-nested-phi-8d31
- base_sha: 112e528906872add2eafe32f8bd1e5eb30c30ee0
- work: prompt/coordination/work/WATER-001/T1-20261106T155244Z-T1-chat-original-builtin-inject-d5f2.json
- scope_commit: 0538a6a2f310bb9f01391c50bdd73af4655ec19c
- injector_source_commit: 6361d9ebd10aab375798eb0c4d8da77f9e59de15
- initial_test_commit: 724f1c82acc9f14c776f0fee959c3a5f5f9fab7a
- synthetic_gate_commit: 0aba4bd7131e9d1994f69c432d5749994c280c67
- initial_real_spirv_run: https://github.com/alwansan/raf/actions/runs/42247669231
- safe_diagnostic_commit: a8f5800af9924f8ea1ba441a11ac7e84ee779a8d
- safe_test_commit: 258d94c26b3f029bd07974bf501bdd718f34ad94
- diagnostic_workflow_commit: b039a973c62c433e14907a2751749799e1564087
- diagnostic_real_spirv_run: https://github.com/alwansan/raf/actions/runs/42248163030
- original_pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385

## Scope and authentic starting evidence

Previous SHA-original preflight [42244565958](https://github.com/alwansan/raf/actions/runs/42244565958) proved three original FFT `OpImageFetch` sites (source/butterfly/butterfly), all coordinate sint32-vector2 and value float32-vector4, free binding3 on set0 and set1, but **no proven GlobalInvocationId Input**. The independently instrumented HLSL-roundtrip candidate produced 384 real keyed reads (64/256/64), 0 key duplicates and 0 OOB in [42242127723](https://github.com/alwansan/raf/actions/runs/42242127723). No independent keyed capture from original SPIR-V exists.

New `scripts/t1_fft_original_global_id_inject.py` is a *private staging-only* SPIR-V assembly transformer. It checks exactly one compute entrypoint, `Shader` capability and Vulkan memory model, reuses existing unsigned32/vector3/Input pointer types or adds them, declares a new Input `GlobalInvocationId` in entrypoint interface, and inserts one **unused OpLoad** in the original entry function after function-local variables. The load is not wired into image sampling, storage, dispatch, thread IDs, or shader output. Original game assets and authored shaders remain untouched. Output marker explicitly says `original_invocation_keyed_buffer_produced=false`.

New synthetic tests validate entrypoint/decoration/type placement, no duplicate builtins, Function OpVariable order, invalid stage/capability/memory model/entry labels, and privacy. Source-only CI [42247488665](https://github.com/alwansan/raf/actions/runs/42247488665) **SUCCESS 100/100 tests** (86 previous plus 14 injection). Private original Vulkan workflow @`202df1439d553849ac9184318ae60510cedd0424` tries `spirv-dis` original slot0, inject, `spirv-as/spirv-val`, temporarily replace original source only in private scratch, execute same-Vulkan output comparator and restore original before rest of tests.

## Actual failure and safe next diagnostic

First original source run [42247669231](https://github.com/alwansan/raf/actions/runs/42247669231) **FAILED** at `Private original dispatch builtin probe could not be proven`, before `spirv-as`; original ZIP2 source staging and tests passed, cleanup passed. The exact failing structural assertion was unknown; do not claim the original shader is invalid.

Added a fixed allowlist of rejection reason categories to the injector, with two tests that prevent exposing any unknown private error text/SSA identifier. Source-only [42248105691](https://github.com/alwansan/raf/actions/runs/42248105691) passed tests. Triggered changed private source [42248163030](https://github.com/alwansan/raf/actions/runs/42248163030); it was in apt setup at checkpoint. Read only `RAFT_T1_ORIGINAL_GID_DIAGNOSTIC` reason and final safe marker, not private source or assembly. If the checker assumption is too strict, add a bounded, source-backed conditional and retest. Never disable validation and never publish raw original data.

## Handoff

- status: waiting_ci; no duplicate active private original run launched
- experiment: prompt/coordination/experiments/T1/20261106T155244Z-T1-chat-original-builtin-inject-d5f2.json (must be updated with actual result)
- canonical event: prompt/coordination/B_TEAM/events/T1/20261106T155244Z-T1-chat-original-builtin-inject-d5f2.json (must reflect verified result)
- next_step: inspect 42248163030 safe error category, fix only demonstrated original-SPIRV difference, then require `spirv-as`, `spirv-val`, and actual same-Vulkan output parity before reporting injected input ready. An unused Input load is not direct original keyed capture, not original-vs-HLSL matching, not Unity authored kernel/Adreno water acceptance. WATER-001 remains OPEN.
