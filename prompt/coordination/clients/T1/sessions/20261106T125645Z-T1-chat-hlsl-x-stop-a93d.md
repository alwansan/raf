# T1 — HLSL-roundtrip FFT butterfly1 X unresolved SSA stop opcode

- session_id: 20261106T125645Z-T1-chat-hlsl-x-stop-a93d
- origin: chat
- issue_id: WATER-001
- status: waiting_ci
- base_sha: 18b47bc7fffc66699f8f0556cd8b478f02dc01fe
- resumed_from_sessions: 20261106T125300Z-T1-chat-hlsl-deep-lane-8e4c; 20261106T124531Z-T1-chat-butterflyx-vector-writer-a6f3; 20261106T1215Z-T1-scheduled-coordinate-overflow-r6q2
- work: prompt/coordination/work/WATER-001/T1-20261106T125645Z-T1-chat-hlsl-x-stop-a93d.json
- scope_commit: 5a57848428d4b75905fcbb86d91d164a818f1664
- source_commit: eb37532378f5ee0b852006a568098db7bf3188d9
- test_commit: 80f9bfdf8b95b4f5bd59bf1e14ae8624b9bcaadc
- workflow_commit: 952c2a3f74f6e2623dc9bcbdbfd6cd3a143421c1
- run_urls: https://github.com/alwansan/raf/actions/runs/42221700354

## Evidence / registered scope

Prior original source [42220554705](https://github.com/alwansan/raf/actions/runs/42220554705) proved butterfly1 X last writer is an OpVectorShuffle fed by OpBitcast(sint32_bits_to_float32) from a signed32 Input vector. Prior translated HLSL compiled candidate [42221101286](https://github.com/alwansan/raf/actions/runs/42221101286) passes but with legal max coordinate-depth12 the translated butterfly1 X still terminates at `unresolved`; this is no longer simply default4 depth_limit. The full-slice includes OpPhi and OpIAdd but cannot link either to the selected X lane. The scheduled T1 coordinate capture comparator now passed 10/10 tests in 42221101286.

New standalone scope registers no other T1 GPU workflow in progress at reservation. Modify `scripts/t1_fft_spirv_read_provenance.py` to add only a fixed-allowlisted `stop_opcode` and `stop_numeric_kind` when a lane has boundary `unresolved`; preserve exact original report for resolved load/constant. Four new source-free `tests/test_t1_fft_spirv_read_provenance.py` cases cover unresolved OpPhi, OpIAdd, unknown custom opcode normalization, and resolved load no metadata. Existing isolated non-Unity original FFT workflow @`952c2a3` reuses full source pin and glslang HLSL compilation.

## Awaiting exact CI

Run [42221700354](https://github.com/alwansan/raf/actions/runs/42221700354) in progress at checkpoint. Check test step then only `RAFT_T1_PASS0_SPIRV_PROVENANCE` after `RAFT_T1_COORDINATE_PROFILE hlsl_roundtrip_slot0`, specifically butterfly site1 X stop. No full Unity/native APK build, original shader edits, original IDs, bit patterns or raw game binaries. Keep WATER-001 OPEN and downstream Unity/Adreno parity unproven.

## Next step

If tests fail, correct minimum diagnostic without weakening privacy. If success, determine whether translated X lane stops at OpPhi or OpIAdd or another operation and plan safe operand-provenance tracing or bitcast correctness proof on the exact original source.
