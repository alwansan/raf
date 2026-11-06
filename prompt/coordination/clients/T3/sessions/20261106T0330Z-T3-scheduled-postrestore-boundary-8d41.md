# T3 scheduled — post-restorer Shader48 provenance boundary (read-only)

- identity: T3; origin: scheduled; session_id: 20261106T0330Z-T3-scheduled-postrestore-boundary-8d41; issue RENDER-002 OPEN / NOT_READY.
- resumed_from_sessions: 20261106T0229Z-T3-scheduled-semantic-ambiguity-a6f2; 20261106T014652Z-T3-chat-particle108-authoredsem-1f83; 20261106T013239Z-T3-chat-particle108-namebridge-6f42.
- baseline HEAD 2f01a235e60a55873b22b5d9ac54fd1afd430a6d (2026-11-06 03:17:42 UTC); independent work file prompt/coordination/work/RENDER-002/20261106T0330Z-T3-scheduled-postrestore-boundary-8d41.json, registration commit 683bf50b398bf2b6f2aa5c7239900a57e8f8fa73.
- owner device feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: artifact 42058825739 world/save/re-entry owner-confirmed; white hand/raft, square smoke, water faults remain; source e9c358eda01785b65e4eb14f18723da426635628; failed publication does not negate phone scenario. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- original source [CI42146385054](https://github.com/alwansan/raf/actions/runs/42146385054) passed 147 tests, 4/4 DXBC original authored VS/FS semantic masks compatible (16 user records/58 lanes); [CI42144978122](https://github.com/alwansan/raf/actions/runs/42144978122) source→roundtrip reflected names 0/46, derived pairs 2/4. Existing uniqueness helper scripts/t3_semantic_location_uniqueness.py is NOT an actual authored semantic mapping.

## Fresh pipeline boundary verification

- Current native workflow .github/workflows/raft-unity-editor-android-import.yml has a post-restorer read-only step named **T3 audit actual post-restoration Material ShaderLab program quality**, running `python3 -m scripts.t3_audit_exported_material_programs` around workflow lines 533–542; this is explicitly `continue-on-error: true`.
- The actual auditor returns `source_original_Shader48_or_same_export_join_performed: false` and `selected_ShaderLab_documents_have_proven_original_programs: false` by design. It checks ShaderLab structural pass completeness and dummy markers plus local Material GUID links; it does **not** join original Particle108/Shader48 identity to post-restorer target nor prove runtime variant authenticity. Therefore a successful build or this JSON alone cannot establish smoke restoration.
- The latest 100 branch Actions run sample had no fresh T3 authentic shader run after original 42146385054. T4's 42153533612 is successful but unrelated. No equivalent native Shader48 post-restorer join was identified in this sampled run list; full historical run enumeration not performed.
- This is a precise **evidence gap**, not proof of a broken Shader48, missing texture, or device failure. No code or asset changes and no new CI requested; no duplicate native build.

## Next actionable experiment

1. Before native Unity import, use authenticated same-export original Particle108 Shader48→Material21 identity and post-restorer GUID mapping in a **private bounded CI stage**. Require unique source Shader identity, exact original source owner pin, and no unproven GUID translation.
2. Record per-target safe counts: dummy marker, pass coverage, original program proof unavailable/available, variant pair mapping and whether Material links to this target. Do not emit shader source, private GUIDs, names, raw DXBC or textures.
3. Only if target and variant mapping are authenticated, test 4/4 derived VS/FS semantic-location correspondence in disposable binaries; reject ambiguous matches using existing unique-bijection helper. No unconditional location rewrite or invented shader program.
4. Coordinate with T3 chat and T5 before editing native workflow or dispatching shared Unity; preserve T4 mouse and T5 Resolution ownership.

Status: scope evidence review complete, NOT_READY, no CI/device claim, no original game content modified. Work can be marked completed after independent audit; actual shader restoration remains OPEN.
