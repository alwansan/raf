# T1 | 20261106T103645Z-T1-chat-storewriters-b4a7

- session_id: 20261106T103645Z-T1-chat-storewriters-b4a7
- origin: chat
- status: active
- resumed_from_sessions: 20261106T101340Z-T1-chat-2f6a; 20261106T1009Z-T1-scheduled-k7m2
- base_sha: 13e03d803b7820d3fabe31cd502abadf20c97be2
- work_id: prompt/coordination/work/WATER-001/T1-20261106T103645Z-T1-chat-storewriters-b4a7.json
- scope_commit: 9939983d9978a3703b6b6bc8228a53b56a4f5ac6
- issue_id: WATER-001
- intended_files: scripts/t1_fft_local_store_writers.py; tests/test_t1_fft_local_store_writers.py; .github/workflows/raft-t1-fft-vulkan-roundtrip-isolation.yml; this session; T1 experiment; T1 event
- experiment_key: water001-t1-original-fft-slot0-spv-local-store-writer-census-base-13e03d8-distinct-from-42196835754-42198180194
- resource_key: t1-fft-vulkan-roundtrip-isolation-ubuntu-24.04-no-shared-unity

## Proven restart

The authenticated Vulkan-vs-Unity trace comparison 42196835754 and promoted-only 42198180194 both found 252/256 site-1 X and 64/64 site-2 coordinate mismatches; source-only integer rewrite fixed site-0 coordinates, but not butterfly coordinates. Site 1 X and site 2 X/Y require further producer provenance. The scheduled 20261106T1009Z evidence-gate CLI hardening is separate; do not touch it. Latest branch had no queued or in-progress Actions at scope time. Owner phone result 42058825739 entered, saved, reopened world; water errors remain. No device water restoration proven.

## Plan recorded before edit

Add bounded direct Function OpStore candidate census at leaf OpLoad coordinate lanes of original FFT slot-0 SPIR-V. No raw SPIR-V IDs, constants, traces, shader bytes, or values in public result. Counts are static, not proof of reaching definitions or authored Unity kernel identity. Source-free adversarial tests and one isolated original Vulkan roundtrip workflow run; no Unity build, mouse/buttons/Settings/audio changes.

## Result — authenticated original-source experiment completed

- Scope code commits: b785211e4d7d5dfcb1bdd69058f81d46f630c951 (private-safe tool), 1136071197449b6e51bc31fc58cd2e7f1c56450c (eight synthetic regression cases), ac6c8c4fb5e7cd2651baabe4d4900f3c6ef93440 (workflow integration).
- Original-authentic CI: https://github.com/alwansan/raf/actions/runs/42204760126 — completed **SUCCESS** at ac6c8c4; job 127848498727. Ubuntu-24.04; bounded private slot0 SPIR-V; ZIP2 recovery and original-layout guard passed. All eight exact-source synthetic tests PASS in Actions; separate local 8/8 PASS.
- No source, SPIR-V identifiers, constants, private shader or raw pixels published. The new public marker reports static opcode/type aggregates only.

| Fetch site | Input role | Direct Function-local OpStore candidates (X and Y) | Stored value types | Immediate producer operation counts |
| --- | --- | --- | --- | --- |
| 0 | source | 3 each | float32 | OpVectorShuffle ×3 |
| 1 | butterfly | 3 each | float32 | OpVectorShuffle ×3 |
| 2 | butterfly | 8 each | float32 | OpVectorShuffle ×7; OpImageFetch ×1 |

- The six observed lane traversals show float32→sint32 bitcast. Each count is **static candidates**, not dominance/reaching-store proof, and X/Y sharing a vector load does not imply identical component provenance.
- Original comparisons https://github.com/alwansan/raf/actions/runs/42196835754 and https://github.com/alwansan/raf/actions/runs/42198180194 found matching butterfly divergences regardless of source-coordinate rewrite. This new evidence rejects a naive assumption of one unambiguous Function-local butterfly writer and directs investigation to control-flow and OpVectorShuffle producers.
- No original authored ComputeShader/kernel identity recovered, no Vulkan↔Unity numerical parity proven, and **no Android/Adreno water fix or new APK**. WATER-001 remains OPEN; no other client's files or Actions touched. Owner world/save/reopen evidence from 42058825739 preserved, with water still malfunctioning.

## Checkpoint links and status

- origin: chat; status: completed (scoped provenance census only)
- experiment: prompt/coordination/experiments/T1/20261106T103645Z-T1-chat-storewriters-b4a7.json
- canonical result event: prompt/coordination/B_TEAM/events/T1/20261106T103645Z-T1-chat-storewriters-b4a7.json
- run_urls: https://github.com/alwansan/raf/actions/runs/42204760126
- branch: feature/android-native-port; no force/no cancellation.

## Next step

Add a bounded *flow-sensitive* def-use check on original private slot0 SPIR-V for the 3 writers of butterfly site1 X and 8 writers of site2 X/Y. Discriminate OpVectorShuffle lane origins and branch/loop reachability before proposing any rewrite. If exact original integer origin can be proved, run a distinct same-input paired Unity/Vulkan numerical control; coordinate Adreno integration with T5. Leave audio, Settings, deferred touch, T4 mouse and T5 UI work untouched.
