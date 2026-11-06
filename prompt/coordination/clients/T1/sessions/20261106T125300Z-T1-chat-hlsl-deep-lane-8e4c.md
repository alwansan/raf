# T1 — original FFT vs HLSL-roundtrip X coordinate lane depth budget

- session_id: 20261106T125300Z-T1-chat-hlsl-deep-lane-8e4c
- origin: chat
- status: waiting_ci
- issue_id: WATER-001
- base_sha: fb17194e8658ac3b2f3fa2fdfdffd991bd730484
- resumed_from_sessions: 20261106T124531Z-T1-chat-butterflyx-vector-writer-a6f3; 20261106T1215Z-T1-scheduled-coordinate-overflow-r6q2; 20261106T123411Z-T1-chat-y-inequal-branch-f52a
- work: prompt/coordination/work/WATER-001/T1-20261106T125300Z-T1-chat-hlsl-deep-lane-8e4c.json
- scope_commit: 2e876f7ca1921e064858b622c358f2f6e6cce791
- workflow_commit: 327c1b6431ad75de2a215c338e91c359e2f0a8f7
- run_urls: https://github.com/alwansan/raf/actions/runs/42221101286

## Verified baseline

Original-private [42220554705](https://github.com/alwansan/raf/actions/runs/42220554705) PASS with X signed-integer Input vector source passed through OpVectorShuffle → OpBitcast(sint32_bits_to_float32) → OpVectorShuffle → full local Function store. The same source-authenticated workflow's HLSL glslang compiled candidate SPIR-V `t1_fft_spirv_read_provenance` recorded coordinate X `depth_limit` with default depth 4. The parser supports max --coordinate-depth 12 and prior source SSA analysis used 12; use this legal upper bound before claiming an actual source type/bitcast loss. Scheduled T1 session `20261106T1215Z` separately tightened capture parser overflow/limits with source tests never run on GitHub.

## New bounded experiment

Own work scope reserved after checking no T1 private-source Actions in progress/queued. Changed only the existing T1 isolated no-Unity workflow to execute `tests/test_t1_fft_coordinate_probe_compare.py` at checkout and to invoke HLSL roundtrip `scripts.t1_fft_spirv_read_provenance --coordinates --coordinate-depth 12` instead of default depth 4. It still SHA-verifies ZIP2 original input, performs no Unity or Android build, does not publish SPIR-V or original shader source, and uses existing 20-minute timeout/concurrency. This is not a numerical replay; it resolves (or preserves) the structural provenance ambiguity and validates comparison parser safety.

## Actual source-authenticated verification — completed

- [GitHub Actions 42221101286](https://github.com/alwansan/raf/actions/runs/42221101286) job `127903059685`, workflow `327c1b6431ad75de2a215c338e91c359e2f0a8f7`: **SUCCESS**. All ten tests from the T1 scheduled `tests/test_t1_fft_coordinate_probe_compare.py` passed, including integer-overflow, byte-size/sample-limit and duplicate/nonfinite controls, and original ZIP2 SHA recovery, HLSL compile, same-Vulkan private roundtrip and scratch cleanup passed.
- Private source pin: `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`. No original game assets, SPIR-V source bytes, literal component indices, or pixel capture released.
- HLSL-roundtrip `coordinate.spv`, **`--coordinate-depth 12`**: Source site0 X/Y reach an `OpLoad` boundary. Butterfly site1 X reaches **`unresolved`**, rather than default-depth4 `depth_limit`; site1 Y reaches a **constant**. Butterfly site2 X/Y unresolved. Butterfly1 whole coordinate slice contains `OpPhi` and `OpIAdd`, plus composite extract/insert, but the generic depth tracer cannot prove which of those is the exact X-lane stopping opcode.
- Previous authenticated original Butterfly1 X source [42220554705](https://github.com/alwansan/raf/actions/runs/42220554705) already showed signed-32 Input vector → shuffle → `OpBitcast(sint32_bits_to_float32)` → shuffle → Function store. The translated X does not yet trace to that boundary, **but this alone is NOT proof the translator changed the number, nor proof of the 252/256 mismatch cause**.
- Experiment: `prompt/coordination/experiments/T1/20261106T125300Z-T1-chat-hlsl-deep-lane-8e4c.json`; canonical event: `prompt/coordination/B_TEAM/events/T1/20261106T125300Z-T1-chat-hlsl-deep-lane-8e4c.json`. Only shared T1 isolated workflow changed. No authored shader rewrite, Unity heavy job, native Android build or changes to T2–T5, audio/Settings/touch.

## Status / handoff

- origin: chat
- status: completed (HLSL-roundtrip depth experiment + scheduled comparator CI)
- run_urls: https://github.com/alwansan/raf/actions/runs/42221101286
- next_step: New independent T1 scoped privacy-safe **actual lane stop opcode** report for HLSL Butterfly1 X at legal depth12; use fixed allowlist and include safe numeric type category, not raw identifiers or component values. Once identified, compare original-vs-compiled SSA Phi/arithmetic path using exact same SHA/input and staged masked coordinate trace. Rewriting shader now would be speculative; WATER-001 remains OPEN.
