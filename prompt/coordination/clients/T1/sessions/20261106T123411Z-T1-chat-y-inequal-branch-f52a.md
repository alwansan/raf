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

## CI state / handoff

Original source experiment run 42219209890 queued after commit 888f2c6, no new Android APK, no Unity heavy build, no T2–T5 files changed. Await source-free test stage, then only aggregate marker `RAFT_T1_FFT_Y_INEQUAL_OPERANDS`. If it fails, repair the minimal source fixture or fail-closed parser, rerun exact changed SHA; if it passes, record source-derived operands and whether condition gates read versus discriminating writer kind. Full Vulkan-vs-Unity numerical parity and Android water still NOT proven.
