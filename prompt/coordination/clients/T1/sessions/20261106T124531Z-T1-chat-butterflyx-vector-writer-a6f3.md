# T1 — original butterfly1 X vector-writer SSA component lineage

- session_id: 20261106T124531Z-T1-chat-butterflyx-vector-writer-a6f3
- origin: chat
- status: waiting_ci
- issue_id: WATER-001
- base_sha: 432dc4b7bc819a49b561e948b471664ee88bd085
- resumed_from_sessions: 20261106T123411Z-T1-chat-y-inequal-branch-f52a; 20261106T122023Z-T1-chat-y-guard-paths-d71e; 20261106T1215Z-T1-scheduled-coordinate-overflow-r6q2
- work: prompt/coordination/work/WATER-001/T1-20261106T124531Z-T1-chat-butterflyx-vector-writer-a6f3.json
- scope_commit: 222af3ca8dfa1f2e520093bde6f8984e7b8b01c7
- code_commit: a0c0587fdb7571fc6421c9e9e8ea9aedc5a792b8
- test_commit: 767898e298ccb5e07d30b9bfcbded19e9fb4d928
- workflow_commit: 00a9157d69ba7bdbca9ba9d9cd1d8881feb1fe3f
- run_urls: https://github.com/alwansan/raf/actions/runs/42220554705
- experiment_key: water001-original-slot0-butterfly1-x-lastwriter-vector-shuffle-ssa-component-lineage-v1-zip2sha15964ea8

## Source-authenticated starting point

Prior original source CI 42211108743 established Butterfly1 coordinate X reads the first physical Function vector component and has a single may-reaching whole-vector `OpVectorShuffle` writer. Prior captured original vs translated coordinate trace showed 252/256 mismatched X at this site; the numerical parity gap is open. CI 42219435992 narrowed the different Y coordinate to false-branch-gated constant path. New experiment focuses X only. Latest scheduled T1 session 20261106T1215Z hardened a coordinate comparator in separate files; no overlap.

## Registered scope / implementation

Reservation created on current HEAD before editing; no T1 roundtrip workflow queued or running then. Added independent `scripts/t1_fft_site1_x_writer_lineage.py` and `tests/test_t1_fft_site1_x_writer_lineage.py`; appended one test-suite line and one exact original slot0 private SPIR-V audit to existing isolated non-Unity T1 workflow. The analyzer enumerates per-instruction CFG last writer identities, distinguishes direct whole vector versus scalar same-physical-lane writes, preserves unknown pointer writes and escapes, then follows only X's component along bounded `OpVectorShuffle`/`OpBitcast`/`OpCompositeConstruct` chains until a load, arithmetic, texture, or unresolved boundary. Reports only source opcode labels, bitcast type families and first/second input selection, never original SSA IDs, literal lane indices, shader bytes, or pixel values.

## Source-authentic CI result — completed

- Actual [run 42220554705](https://github.com/alwansan/raf/actions/runs/42220554705) job `127901229510`, at workflow commit `00a9157d69ba7bdbca9ba9d9cd1d8881feb1fe3f`: **SUCCESS**, 16/16 new adversarial tests passed, SHA-verified ZIP2 original FFT source recovery, private Vulkan roundtrip and scratch removal passed.
- Original source pin: `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Nothing original (SPIR-V raw bytes, source shader, identifiers, private numeric values or pixel trace) exported.
- Original slot0 **Butterfly1 X** reads physical component X. Of three static writes affecting this component, the bounded actual CFG may-path model permits **one last whole-vector writer**, with no uninitialized/unknown index/pointer escape path in this bounded Function-local analysis.
- The sole writer's direct value opcode is `OpVectorShuffle`. Tracing *selected X component* through source SSA produces:
  `OpVectorShuffle` → `OpBitcast (sint32_bits_to_float32)` → `OpVectorShuffle` → `OpLoad` from **Input storage holding signed 32-bit integer vector**. The outer and inner shuffles select second and first vector input respectively (no numeric component indices exposed).
- This now identifies an *original bit-preserving signed integer coordinate carrier* feeding X via whole-vector store. It does not prove the runtime numeric value, the HLSL/glslang bit interpretation, correct Unity authored kernel identity, or Vulkan↔Unity per-coordinate parity. Earlier dynamic comparison found **252/256 mismatched X coordinates at butterfly1** and remains unresolved. No original shader rewrite, Unity Editor run, native build, or Adreno acceptance claimed.
- Experiment JSON: `prompt/coordination/experiments/T1/20261106T124531Z-T1-chat-butterflyx-vector-writer-a6f3.json`; canonical result event: `prompt/coordination/B_TEAM/events/T1/20261106T124531Z-T1-chat-butterflyx-vector-writer-a6f3.json`. No other agents' files, audio/Settings or deferred touch changed.

## Status / handoff

- origin: chat
- status: completed (bounded original butterfly1 X writer provenance)
- run_urls: https://github.com/alwansan/raf/actions/runs/42220554705
- next_step: probe the **compiled HLSL-roundtrip candidate X coordinate SSA lane** at `$TMPDIR/coordinate.spv` with a deeper bounded but source-safe producer tracer and compare original signed-Input bitcarrier signature vs translation. The existing `scripts/t1_fft_spirv_read_provenance.py` reports depth_limit under default 4 for translated source; test explicit legal 12 depth before implementing new conversion logic. Follow with same-input paired coordinate-keyed Vulkan/Unity evidence using the updated scheduled comparator, then modify HLSL only if a specific transformation loss is proven. WATER-001 remains OPEN.
