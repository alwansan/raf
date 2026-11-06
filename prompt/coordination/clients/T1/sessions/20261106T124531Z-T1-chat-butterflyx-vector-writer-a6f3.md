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

## CI checkpoint

Run [42220554705](https://github.com/alwansan/raf/actions/runs/42220554705) triggered by workflow commit 00a9157. Exact-source result awaits runner validation. Source-free tests cover first/second shuffle input, integer bit reinterpretation, Function-load and arithmetic boundaries, branch overwrites, loop, unreachable writers, x/y alias isolation, unknown dynamic alias, pointer escape, malformed CFG and output privacy. No original Unity kernel identity, numeric parity, Android/Adreno water or game runtime fix claimed. WATER-001 remains OPEN.

## Next step

Check test gate, repair minimal failures if any, then read only source-safe `RAFT_T1_FFT_BUTTERFLY_X_WRITER_LINEAGE` summary. Preserve code/method constraints and note whether the X writer chain ends in signed/float bitcast, texture fetch, Function load or arithmetic boundary. Save experiment/event/work completion for scheduled T1. Do not modify original shader based solely on static producer evidence.
