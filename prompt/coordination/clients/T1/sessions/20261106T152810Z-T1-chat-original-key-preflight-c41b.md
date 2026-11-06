# T1 — original SPIR-V keyed capture prerequisite preflight (source-free)

- session_id: 20261106T152810Z-T1-chat-original-key-preflight-c41b
- origin: chat
- status: completed (source-free readiness tool only)
- issue_id: WATER-001 OPEN / NOT_READY
- resumed_from_sessions: 20261106T151730Z-T1-chat-keyed-candidate-3a7f; 20261106T1511Z-T1-scheduled-invocation-cli-k7m2; 20261106T1408Z-T1-scheduled-pair-input-readiness-v3
- original_source_pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 (not loaded in this source-only experiment)
- base_sha: c2d1d93c96e47c0e60551395380da2e93327d560 (further concurrent peer commits are allowed)
- work: prompt/coordination/work/WATER-001/T1-20261106T152810Z-T1-chat-original-key-preflight-c41b.json
- scope_commit: eb89f816f0f122090f7acebd03ee46cb94634457
- source_commit: bb50bc7d06d3031e834bf1b8aaf43002555e96fd
- tests_commit: 84b012871519a79b51fbb8f16cb7e0e91bdfb8e6
- workflow_commit: cca8e8d3e7a455173225653c209a67737c9a810a
- privacy_fixture_fix: a64b0f89b0b7b52ba24b322fde71b8fd35e7511d
- failed_source_only_run: https://github.com/alwansan/raf/actions/runs/42243651596
- passed_source_only_run: https://github.com/alwansan/raf/actions/runs/42243693907

## Distinct scope / verified hypothesis

Scheduled session 20261106T1408Z correctly determined no independent SHA-authenticated original-and-candidate keyed invocation traces were retained. Current earlier chat session `20261106T151730Z-T1-chat-keyed-candidate-3a7f` is executing a new candidate-only `--invocation-keys` trace from original-derived HLSL in private Vulkan CI `42242127723`; that job was still in its apt step when this scope started. This separate source-only work does not touch its workflow/runner.

New `scripts/t1_fft_original_keyed_preflight.py` provides a privacy-safe original SPIR-V prerequisite audit **without modifying the shader**, examining at most 60,000 instructions and 16 image-read sites. It checks exactly 3 expected source/butterfly/butterfly `OpImageFetch` roles, typed signed/unsigned vector coordinate widths, typed fetch values, `GlobalInvocationId` as either direct or valid Input struct member in a compute entry point interface, and whether descriptor set 0 or 1 binding 3 is currently occupied. Reports only finite type families, counts and booleans, not source IDs, offsets, literal values or original shader bytes. Crucially it explicitly returns `direct_original_spirv_instrumented=false`, `original_invocation_capture_proven=false`, `paired_numeric_parity_proven=false`.

Added `tests/test_t1_fft_original_keyed_preflight.py` 12 source-free regression tests: original roles and dispatch input, signed int2 and float4, descriptor set 0/1 collisions, hidden interface, wrong input type, struct-member BuiltIn GlobalInvocationId, invalid float coordinate, wrong role order, duplicate decorations, fourth fetch, and output privacy.

## Tested CI

First [run 42243651596](https://github.com/alwansan/raf/actions/runs/42243651596) **failed one privacy fixture expectation** because it accidentally asserted the public schema word `coordinate` was absent, while `coordinate_type` is a valid output key. Fixed test-only expectation to ensure the **private symbol `%coordinate`** is absent, without changing the tool output or parsing code.

Corrected [run 42243693907](https://github.com/alwansan/raf/actions/runs/42243693907) **SUCCESS**, 86/86 tests: 20 strict pair + 11 coordinate probe + 9 invocation trace + 14 nested Phi + 7 scheduled ULP + 5 scheduled CLI + 8 candidate keyed + 12 original preflight tests. This is only synthetic validation against fixtures. **No authentic original SPIR-V source was opened in this CI**. The long source-authentic Vulkan candidate job `42242127723` remains independent; do not cancel or assume its result.

## Handoff

Next original-source private runner opportunity: run `python3 -m scripts.t1_fft_original_keyed_preflight "$TMPDIR/candidates/_private_vulkan/slot0.spv"` only under exact SHA-verified ZIP2 source recovery, after checking active T1 private Vulkan jobs; read sanitized `RAFT_T1_ORIGINAL_KEYED_PREFLIGHT`. If original Input builtin or binding is unavailable, require separate proven instrumentation plan; do not fabricate one. An original SPIR-V instrumentation, independently signed/shader-source-matched run and strict pair gate are **not yet delivered**. A correct source/candidate numeric comparison and Android water acceptance remain future evidence requirements, not current status.

No game shaders, Unity workflows, Android APK, audio/Settings, deferred touch or T2–T5 source changed; no other jobs cancelled or forcibly overwritten. Water remains OPEN / NOT_READY.
