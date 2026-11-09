# T3 scheduled scope — authentic semantic provenance negative result

session_id: 20261109T2134Z-T3-scheduled-smoke-semantic-no-proof-x6k2
origin: scheduled
base_sha: b90e9ac968ca2d71902b7edda9919fdbee6ebbe9
issue: RENDER-002 OPEN / NOT_READY 0/3
experiment_key: t3-smoke34-real-spv-usersemantic-absence-decision-20261109
resource_key: no shared GPU/Unity/ZIP2 allocation; read-only CI evidence
files_owned: this work file and clients/T3/sessions/20261109T2134Z-T3-scheduled-smoke-semantic-no-proof-x6k2.md only

## Coordination and inherited evidence
Latest T3 chat 20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2 and scheduled 20261109T2035Z-T3-scheduled-semantic-location-gate-m6q8. T1/T2 water, T4 mouse, T5 display/build; no overlap. This scope is a decision on authentic evidence, not a repeated extractor run. B-era source facts retained and credited; no B reactivation.

## Falsifiable decision
CI42696526193 succeeded (57 synthetic checks, genuine SHA-original two DXBC PS permutations and private SPIR-V extraction). Both original and roundtrip SPIR-V have zero HlslSemanticGOOGLE labels and no SPV_GOOGLE_hlsl_functionality1. Thus a semantic-name decoration-based source-to-SPV provenance route is unavailable for these exact programs. Numeric DXBC register = SPV location candidates 7/7 original, 5/7 roundtrip; this is insufficient as proof of lane dataflow, especially with changed locations. The nine source-free mapping-gate checks ran as part of 57 tests; passing tests are not an authenticated lane mapping. Original 22 used lanes vs 28 declared; reflection 28 declared is not evidence of dropped lanes.

Decision: DO NOT feed numeric candidates to the structural bijection validator as authenticated mappings, DO NOT claim recovered shader or smoke pixel fix, and DO NOT rerun the identical annotation census. Next experiment must trace DXBC input operand to vkd3d emitted SPV ID/Location via compiler dataflow or instrumented translation, with private data and aggregate-only output. Then compare alpha blend/pass and actual pixels against CL phone smoke. No native APK or other team resource consumed.

Source evidence: https://github.com/alwansan/raf/actions/runs/42696526193 ; https://github.com/alwansan/raf/actions/runs/42692895633 ; https://github.com/alwansan/raf/actions/runs/42691211652 ; https://github.com/alwansan/raf/actions/runs/42689814110
