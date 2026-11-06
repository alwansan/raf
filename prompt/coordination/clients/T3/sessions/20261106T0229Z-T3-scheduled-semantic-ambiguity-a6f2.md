# T3 scheduled — conservative unique varying-location bijection guard

- identity: T3; origin: scheduled; session_id: 20261106T0229Z-T3-scheduled-semantic-ambiguity-a6f2
- issue: RENDER-002 OPEN; readiness: NOT_READY
- baseline branch HEAD: e50abe7c36759117a0c5092ab90ba90500dff653
- independent work registration: prompt/coordination/work/RENDER-002/20261106T0229Z-T3-scheduled-semantic-ambiguity-a6f2.json at commit 1df5b025b5e6a312a777874406653d606eebdafe
- resumed_from chat 20261106T014652Z-T3-chat-particle108-authoredsem-1f83 and scheduled 20261106T0131Z-T3-scheduled-io-order-6d9a.
- original source evidence CI42146385054: four original VS/FS DXBC authored semantic-mask pairs matched; source-to-roundtrip compiler names 0/46, HLSL roundtrip VSFS pairs only 2/4. This proves no automatic by-name or by-type location rewrite is justified.
- hypothesis: even where type/component compatibility candidates exist, location rewrite must reject multiple feasible bijections rather than selecting an arbitrary permutation.
- implementation: scripts/t3_semantic_location_uniqueness.py, commit dd90874df6f2944026a9c57813164b986deb0911; exact bounded integer-location bipartite matching with zero-or-many => None. No private semantic names or game data.
- regression: tests/test_t3_semantic_location_uniqueness.py commit d793c81c898c01d0089dfc4250e7026ae144511c; 7 local Python unittest cases PASS: unique, ambiguous, Hall violation, forced unique, invalid booleans/ranges, unbalanced, empty.
- experiment key: T3-sourcefree-semantic-location-unique-bipartite-proof-v1. No CI dispatch, no source ZIP2 acquisition, no Unity build; shared resource none. Source-only diagnostic helper, not wired to original shader remap or game runtime.
- device feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: owner verified world/save/re-entry on artifact 42058825739; white hand/raft and square smoke remain. No phone verification here. T4 mouse and T5 resolution/three buttons untouched.
- follow-up: obtain authenticated per-stage original DXBC semantic-to-SPIR-V Location and HLSL authored semantic candidate edges for each exact keyword pair; feed only independently proven edges to this guard; reject any ambiguous variant, and only then consider disposable SPIR-V remap and spirv-val/VSFS interface validation. Coordinate with chat T3 before touching its live source files. Existing source program comparison remains 2/4 derived pairs and no pixel parity claim.
- scope status: source-free guard implemented and locally tested; GitHub CI on new commits not yet confirmed; RENDER-002 remains OPEN.
