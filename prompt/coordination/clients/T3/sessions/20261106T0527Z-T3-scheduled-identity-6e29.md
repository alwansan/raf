# T3 scheduled — Shader48 structural provenance gate

- identity: T3; origin: scheduled; session_id: 20261106T0527Z-T3-scheduled-identity-6e29
- issue: RENDER-002 OPEN / NOT_READY
- baseline SHA: 0583fb3df8b4e656868e747a101da7aa24031ef8
- scope registration: edc9d2f176169ebb5b31e0a3c04dc31b8f2dc5cf
- implementation: 25ed28581e572fb0e947c288ba54bdbfa43ea912; tests: 19b90dc0fd61e520d8ff8b59e4b6315b4342fb9f
- resumed_from_sessions: 20261106T0431Z-T3-scheduled-postrestore-gate-6f2c; 20261106T0330Z-T3-scheduled-postrestore-boundary-8d41; prior chat Particle108 sessions.
- owner phone evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739/e9c358eda01785b65e4eb14f18723da426635628. World/save/reentry confirmed by owner, not a shader fix. CL pinned snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- new bounded tool: scripts/t3_shader_identity_gate.py accepts a SHA256-pinned source ID and *separately authenticated* exported ShaderImporter GUID manifest, checks actual post-restorer .shader.meta and all explicitly scoped .mat references, rejects placeholder marker, mismatched GUID, missing links, symlink and path traversal. Outputs only aggregate STRUCTURAL_LINK_ONLY and explicit false authenticity/pixel claims.
- tests: six synthetic unittest cases locally PASS (0.010s) for structural link, GUID mismatch, dummy marker, path traversal, unpinned input, broken material. Tests were first executed on equivalent standalone source in this run; repository CI NOT YET VERIFIED.
- important limit: manifest original-to-export identity join is an **input assertion**, not discovered or proven by this tool. A malicious or mistaken manifest can still assert a false source ID; do not claim original Shader48 verified. This is a guard for the next private same-export experiment, not a shader or phone repair.
- no raw assets, .meta, Unity, audio, Settings, mouse, resolution or native build changed; no Action cancelled or duplicated.
- next: validate six repository tests in cheap CI, then obtain independently verified Shader48/Particle108 original-to-export mapping from SHA-pinned same-export evidence and run this gate on *post-restoration* material/shader files. Compare selected program variants and texture links, only then propose pixel repair.
