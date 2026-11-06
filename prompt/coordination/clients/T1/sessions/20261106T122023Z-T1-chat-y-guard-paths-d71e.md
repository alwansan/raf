# T1 — butterfly-1 Y typed branch-path witness

- session_id: 20261106T122023Z-T1-chat-y-guard-paths-d71e
- origin: chat
- status: waiting_ci
- issue_id: WATER-001
- base_sha: 4bfe352226792fcf5e8356fe621a4376a6d343f3
- resumed_from_sessions: 20261106T113707Z-T1-chat-bitcarrier-producer-c8f1; 20261106T113001Z-T1-chat-lane-alias-f73c; 20261106T1215Z-T1-scheduled-coordinate-overflow-r6q2
- work: prompt/coordination/work/WATER-001/T1-20261106T122023Z-T1-chat-y-guard-paths-d71e.json
- reservation_commit: ca3046a9d9b87cad8ed830c8dca6195bddfd8064
- source_commit: 0548a7e3ca93b56af28def87a94bf375a3dffb37
- pointer_escape_hazard_commit: 1970eb99d1f7826cfcefb12cad548655b9d24f92
- tests_commits: 06810b3de1ad37c13bc32ffc9a2e75c058f418d2; 5824cba6b5dd8f3a9b97940a10198fcc0d4aafb8
- workflow_commit: 035c2a943364ed8bc6129afae368283d2172c002
- run_urls: https://github.com/alwansan/raf/actions/runs/42217597416
- experiment_key: water001-original-slot0-butterfly-site1-y-cfg-branch-pathtyped-last-writer-v1-zip2sha15964ea8

## Authenticated baseline

Last original FFT source CI 42212055131 passed 13/13 and original private slot0 SPIR-V. Butterfly1 Y reads a physical Function-local vector component beyond X/Y. Its per-lane may-reaching writers are one signed-32-bit-bit-pattern-to-float bitcast and one float constant; source-only dataflow had not proven whether they can execute on the *same* control-flow path or which branch predicates influence each last write. The scheduled session 20261106T1215Z independently hardened the coordinate-keyed capture reader and did not run repo tests; these files are separate.

## New scoped implementation

Registered own work scope on HEAD after checking no T1 GPU workflow queued/running. Added `scripts/t1_fft_site1_y_branch_paths.py` and `tests/test_t1_fft_site1_y_branch_paths.py`. Enumerates finite abstract per-function basic-block paths (bounded, fail-closed), records which typed writer can be *last* at the target load and whether a path may have visited both bitcarrier and constant, plus safe opcode families for encountered branch predicate producers. An observed branch predicate opcode is **not** proof it chooses that writer or that a dynamic GPU invocation takes that path. Captures possible pointer escape separately from latest direct writer. Original SPIR-V and literal data never enter public artifacts/logs. Existing T1 isolated 20min source-authentic Vulkan workflow updated to run synthetic tests then private original analysis.

## CI state and next steps

One distinct CI run 42217597416 is in progress. No Unity Editor or Android build started, and T2–T5 scopes/audio/Settings/touch untouched. After CI validate only synthetic tests and `RAFT_T1_FFT_BUTTERFLY_Y_GUARD_PATHS` bounded original marker. If failed correct minimal parser/test, rerun exact changed source. If passed record branch path reachability and limitations. Do not claim Vulkan↔Unity numerical parity or water restored. WATER-001 remains OPEN.
