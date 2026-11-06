# T3 scheduled — 20261106T1828Z-T3-scheduled-contract-fixture-b6e1

- origin: scheduled
- issue: RENDER-002 OPEN / NOT_READY
- baseline HEAD: ac61f1e6fe26a8f23213f67acc5a5e065046773f
- scope lease: c50132d3172f6838e1e4c757ad40761b9c0235ed
- source commit: cf75fe9b51a4f338f72d4e90a1286244560f5a8f
- test commit: 74a29708989cd78ba4302a277ed028eebb8805d5
- owner report: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone world/save/reentry is only established for artifact 42058825739, not current HEAD.
- resumed from: 20261106T1734Z-T3-scheduled-crosscontract-a71c; T3 chat 20261106T1818Z-T3-chat-shaderlab-prop-contract-37bd (separate ShaderLab property scope).
- trial vote: T3 «لا يحتاج» in trial-20261106-r1; source-only diagnostics are not a major Android graphics integration.

## Actual change
Added a standalone source-free DXBC/SPIR-V contract checker and seven synthetic unittest fixtures. Contract requires explicit provenance (stage, resource family, DX register, descriptor set/binding, array count), detects missing mappings, duplicate targets, array span and stage mismatch. Equal numeric registers/bindings are deliberately insufficient. No raw game resources or bytecode published.

## Verification and limits
GitHub commits above confirm publication, but Python tests have NOT been executed in this session. No private original DXBC↔SPIR-V provenance was available to this synthetic check, so no actual Shader48 binding match, ShaderLab repair, Unity compilation, device pixel or smoke causality is claimed. Follow-up: run `python3 -m unittest tests.test_t3_dxbc_spirv_contract_join` or discoverable unittest runner, then connect private pinned Shader48 RDEF to translated SPIR-V reflection with stage/keyword identity, provenance and count-only reporting. The first real mismatch should drive targeted ShaderLab program repair, not blanket material/GUID rewrites.

Preserved T4 mouse and T5 Resolution/buttons scopes, .meta/GUID/.rgd, FMOD and Settings. No native build, workflow dispatch or cancellation.
