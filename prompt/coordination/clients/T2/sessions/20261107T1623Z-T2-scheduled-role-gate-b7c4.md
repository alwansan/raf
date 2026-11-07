# T2 scheduled — safe per-pass Foam role gate

- session_id: 20261107T1623Z-T2-scheduled-role-gate-b7c4
- origin: scheduled
- issue: WATER-001; status: completed_source_only
- base HEAD: 1e2f2023a3959efd18f4e3c9a2cf63764c37e2c0
- work registration: 89778f9beeaf1de0e64d98f055b87266ba85d96c
- source: 52d54e73fc468c083f5599a017fc5ae793528351
- tests: b64f0316800d7b5147e63b1688be89fe089c5978
- origin evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, original pass correlation CI 42308583977; previous scheduled 20261107T1518Z and chat 20261107T2227Z.
- experiment_key: T2-safe-pass-role-gate-v1
- no shared GPU/Unity resource.

## Verified evidence and boundaries

Owner's artifact 42058825739 enters/saves/reopens a world; publishing failed, water pass/FFT errors remain. Original static Mono.Cecil analysis reports pass0 RenderTexture->RenderTexture and pass1 unknown->unknown; this does not imply pass1 has no textures.

Added independent `scripts/t2_foam_pass_role_gate.py` and `tests/test_t2_foam_pass_role_gate.py`, leaving the chat-owned original scanner, shaders, metadata and native workflow untouched. Gate rejects duplicated pass IDs, malformed types, unexpected fields (including possible private identifiers), unknown roles and non-two-site input; prints only allowed aggregate categories. Local standalone copy passed three unittest methods (including eight adversarial subcases); this was not a repository checkout or original Mono.Cecil test. No GitHub Actions dispatched, no Unity build, no device proof. Existing source-only runs inspected: 42373576551/554/606 completed success. No equivalent active run observed in the inspected latest page.

## Next step

Integrate this validator as a pre-publication check in the existing T2 safe report producer only after inspecting current report schema and coordinating with chat-owned files. On original pinned source, distinguish pass1 unknown producer reason without publishing names or IL; then address CB0/ShaderLab and device validation with T1/T3. WATER-001 OPEN; trial build vote unchanged.
