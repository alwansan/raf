# T1 — original FFT butterfly Y OpINotEqual typed predicate and branch gate

- session_id: 20261106T123411Z-T1-chat-y-inequal-branch-f52a
- origin: chat
- status: waiting_ci
- issue_id: WATER-001 / OPEN
- base_sha: 5d462bbbee3d2ddb8352203f60646a43679659d9
- resumed_from_sessions: 20261106T122023Z-T1-chat-y-guard-paths-d71e; 20261106T113707Z-T1-chat-bitcarrier-producer-c8f1; 20261106T1215Z-T1-scheduled-coordinate-overflow-r6q2
- work: prompt/coordination/work/WATER-001/T1-20261106T123411Z-T1-chat-y-inequal-branch-f52a.json
- scope_commit: d8d4b3f3132b8eb0bb2015b78579be90d9d87a7b
- source_commit: e2f6c08bd632a4d9d348691053a2665b19abf641
- test_commit: e69c86f579dd6b5bb8b2caea777df95f9ec14e68
- workflow_commit: 888f2c6f2167989f87dff73bc872cb876eb24745
- run_urls: https://github.com/alwansan/raf/actions/runs/42219209890

## Previous evidence and independent question

The last original source CI 42217830589 passed. Butterfly1 Y has 5 static Function-local writers, but the source-backed bounded CFG path explorer permits only a float constant as the last writer at this precise fetch. A conditional predicate producer `OpINotEqual` occurs on the path. This does not prove predicate truth at runtime, image coordinate numerical fidelity, or why original vs translated Unity FFT differs. The latest scheduled T1 task is separate coordinate parser overflow hardening; no overlapping files or running T1 GPU job at scope reservation.

## New code

New `scripts/t1_fft_site1_y_inequal_source.py` treats original SHA-pinned private SPIR-V `OpINotEqual` branches as typed predecessor operands. It classifies operand scalar/vector kinds and producer opcodes, then explores true/false CFG suffixes with bounded may-reaching scalar writers. A branch can `gate` this read, or both successors may reach the read with possibly different writers. This DOES NOT evaluate dynamic branch truth, prove a particular input, or publish original SSA IDs, shader bytes, integer literal/pixel contents. Added `tests/test_t1_fft_site1_y_inequal_source.py` for true/false gating, writer discrimination, branch joins, loops, dynamic aliases, escapes and malformed source. Existing isolated T1 non-Unity Vulkan workflow runs new synthetic tests and original-private audit.

## Exact-source CI results and limitations — completed

- First [run 42219209890](https://github.com/alwansan/raf/actions/runs/42219209890) failed before accessing original input: 13/14 synthetic tests passed, one malformed branch (OpBranchConditional before end of block with missing target) reached a raw KeyError. Added deterministic ValueError rejection for nonfinal terminators and nonexistent successors in source fix `3dd79472e5ae998554c122ba71acee7a5e74887a`.
- Corrected [run 42219435992](https://github.com/alwansan/raf/actions/runs/42219435992), job `127897502697` @ `fc3598e1f3c7cffea41d2f9db9ccdf872274083e` **SUCCESS**; 14/14 new synthetic unit tests, original SHA-pinned ZIP2 recovery, private original FFT slot0 source SPIR-V, same-Vulkan isolation and scratch cleanup all completed.
- Original private FFT butterfly site1 Y: *one relevant conditional* `OpINotEqual`. Its **two input types are uint32**, with producer opcode families `OpBitcast` and `OpConstant` respectively; no comparison literal or IDs exported.
- **FALSE successor** can structurally reach the image fetch and has no new post-branch writer (`possible_last_writes_since_branch=["prior_writer"]`). **TRUE successor** cannot reach the image fetch. Thus this predicate guards *whether the original fetch can occur*, rather than acting as a direct bitcarrier-versus-float Y writer selector in this bounded CFG model.
- Combine strictly with previous [CI 42217830589](https://github.com/alwansan/raf/actions/runs/42217830589): at the actual Butterfly1 Y read, the prior last writer in the full-path model is a **float32 constant**, not a signed-bitcarrier write. The independent suffix model cannot prove the exact prior value by itself.
- `dynamic_truth_proven=false`, `numeric_parity_proven=false`. These are potential CFG paths; no original comparison *values*, branch runtime truth, Unity ComputeShader authored identity, exact original↔Unity numeric parity, or Android water pixels were verified. The original source identity is pinned to `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385` and original private bytes were never published.
- Experiment: `prompt/coordination/experiments/T1/20261106T123411Z-T1-chat-y-inequal-branch-f52a.json`. Canonical event: `prompt/coordination/B_TEAM/events/T1/20261106T123411Z-T1-chat-y-inequal-branch-f52a.json`. No original shader/asset source rewritten, no Unity/Android build started, audio/Settings preserved, deferred touch and T2–T5 scopes unchanged.

## Final status / handoff

- origin: chat
- status: completed (scoped original Y predicate input + read-gating analysis)
- run_urls: https://github.com/alwansan/raf/actions/runs/42219209890 ; https://github.com/alwansan/raf/actions/runs/42219435992
- next_step: Prioritize original Butterfly1 **X**, whose earlier original-versus-Unity trace had 252/256 mismatched X coordinates. Track its whole-vector `OpVectorShuffle` writer source component and signed/float bit reinterpretation under private exact source pin. Use same-input pinned Vulkan/Unity coordinate-keyed capture and independent comparator from latest scheduled session before any HLSL/ComputeShader rewrite; keep WATER-001 OPEN until actual Unity/Adreno parity evidence.
