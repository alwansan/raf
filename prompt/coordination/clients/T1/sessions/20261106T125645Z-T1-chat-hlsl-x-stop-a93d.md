# T1 — HLSL-roundtrip FFT butterfly1 X unresolved SSA stop opcode

- session_id: 20261106T125645Z-T1-chat-hlsl-x-stop-a93d
- origin: chat
- issue_id: WATER-001
- status: completed (scoped Phi stop-opcode investigation)
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

## Actual test gate / original CI pending

Run [42221700354](https://github.com/alwansan/raf/actions/runs/42221700354) checked source commit `952c2a3f74f6e2623dc9bcbdbfd6cd3a143421c1`. **Synthetic tests step PASSED** (including 4 new stop opcode cases and prior regression suites). The GitHub Actions original Vulkan stage **remains in progress** while dependencies install; no authenticated final HLSL butterfly1 X `stop_opcode` result is asserted yet.
- Experiment: `prompt/coordination/experiments/T1/20261106T125645Z-T1-chat-hlsl-x-stop-a93d.json` (waiting_ci).
- Canonical progress event: `prompt/coordination/B_TEAM/events/T1/20261106T125645Z-T1-chat-hlsl-x-stop-a93d.json`.
- Work status: waiting_ci; actual runner resource may remain in use until run completion. No other T1 run was cancelled, no original shader/Unity/native APK modification made. WATER-001 OPEN / NOT_READY.

Next: inspect terminal status and safe `RAFT_T1_PASS0_SPIRV_PROVENANCE` marker following `RAFT_T1_COORDINATE_PROFILE hlsl_roundtrip_slot0`. Record actual site1 X `stop_opcode` and `stop_numeric_kind` only if original private HLSL stage passes; if installation fails, report runner failure instead of claiming shader semantics. Then update this own session/experiment/event/work as completed or blocked, without running an equivalent duplicate job.

## Next step

If tests fail, correct minimum diagnostic without weakening privacy. If success, determine whether translated X lane stops at OpPhi or OpIAdd or another operation and plan safe operand-provenance tracing or bitcast correctness proof on the exact original source.

## Verified final CI result (follow-up)

[GitHub Actions run 42221700354](https://github.com/alwansan/raf/actions/runs/42221700354) job 127905081188 **COMPLETED SUCCESS**. Initial apt dependency installation was slow but ultimately completed; source-free tests, ZIP2 immutable source recovery, original-and-translated Vulkan stages, private scratch cleanup all passed. Source pin remains `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

The first butterfly read's translated **X** is specifically `boundary=unresolved, stop_opcode=OpPhi, stop_numeric_kind=float32`, at coordinate-depth 12. The second butterfly X and Y also stop at `OpPhi float32`. Source image X and Y reach `OpLoad`. The OpIAdd in the whole slice cannot be attributed to X by the original generic opcode census; the new direct-lane stop establishes Phi, not a numeric root cause.

No original SSA IDs, private original shader assets, numerical constant bits or GPU pixel data were published. A Phi merge alone does not prove incorrect HLSL conversion; original-vs-translated same-input invocation trace and authored Unity/Adreno runtime evidence remain absent. WATER-001 **OPEN / NOT_READY**.

Work and experiment status updated to completed; canonical event promoted to result. The distinct source-only paired-evidence gate is developed by a separate T1 chat session `20261106T130729Z-T1-chat-pair-gate-6c2e` with CI 42223419922. Next investigation should classify typed Phi inputs/predecessors before any speculative shader rewrite.
