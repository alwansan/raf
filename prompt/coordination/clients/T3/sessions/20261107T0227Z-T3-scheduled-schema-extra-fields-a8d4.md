# T3 scheduled — mixed reflection coordinate guard

- session_id: 20261107T0227Z-T3-scheduled-schema-extra-fields-a8d4
- origin: scheduled; identity: T3; track: RENDER-002 OPEN / NOT_READY.
- Owner report: docs/DEVICE_FEEDBACK_42058825739_AR.md. Phone Artifact 42058825739 entered/saved/exited/re-entered world; white raft/hand, lighting and square smoke persist. CL source pin 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Do not claim graphics or device repair.
- Intake HEAD: 546fe71aad5981befbed8115789104678a54f816. Reviewed AGENTS, current owner requirements, STATUS, T_TEAM protocol/operating instructions, previous scheduled 20261107T0125Z-T3-scheduled-ci-proof-n6c2 and chat 20261106T2252Z-T3-chat-keyword-routed-61e9. Latest listed CI42318375479 success on older SHA 55b39631; no active/queued runs among latest eight returned.
- Independent scope registered BEFORE source edit: [work file](../../../../work/RENDER-002/20261107T0227Z-T3-scheduled-schema-extra-fields-a8d4.json) commit f54dfca4. No shared GPU/Unity resource.
- Reproduced by code-path reasoning: DX reflection row with unexpected `set` but no `binding` passed the minimum schema then indexed `binding`, causing KeyError instead of a diagnostic. SPV rows with extra `register` also have ambiguous namespace.
- Source guard commit b7f5c1aa rejects mixed coordinate namespaces as `invalid_schema` before numeric key construction. Synthetic regression commit 2cf8ddc6 adds four tests (one valid, three invalid). Work checkpoint 7d658861.
- Verification boundary: local environment could not access GitHub raw over DNS, and new Python tests were not executed. Older CI42318375479 does NOT validate this patch. No CI dispatched, Unity build, asset replacement, .meta/GUID/.rgd change, or device test.
- Next: execute `python3 -m unittest discover -s tests -p 'test_t3_dxbc_spirv_contract_join*.py' -v` on SHA including 2cf8ddc6; verify live HEAD first, then use authenticated private Shader48 provenance to map RDEF↔SPV, original Material/ParticleRenderer and CL screenshots. Avoid duplicating chat ShaderLab work and T4/T5 scopes.
- Trial vote remains لا يحتاج until substantive phone-testable graphics repair is integrated. RENDER-002 OPEN / NOT_READY.
