# T3 scheduled — Shader48 post-restoration identity gate

- identity: T3; origin: scheduled; session_id: 20261106T0431Z-T3-scheduled-postrestore-gate-6f2c; issue RENDER-002 OPEN / NOT_READY.
- baseline HEAD: 4506c4d0afa298947bc7a116a8a0c8c722a97fbc; scope registration commit 9e37c115a6f45695f3acafc4c110707f6a5322cc.
- scope: prompt/coordination/work/RENDER-002/20261106T0431Z-T3-scheduled-postrestore-gate-6f2c.json; read-only audit, no shared Unity resource.
- resumed from 20261106T0330Z-T3-scheduled-postrestore-boundary-8d41 and 20261106T0229Z-T3-scheduled-semantic-ambiguity-a6f2, plus earlier chat particle108 sessions. Historical state.json and MEMORY.md are stale relative to these session files; left untouched.

## Fresh evidence

Owner's docs/DEVICE_FEEDBACK_42058825739_AR.md pins 42058825739/e9c358eda01785b65e4eb14f18723da426635628 and CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Phone world/save/re-entry was successful, delivery publication failed, and white hand/raft and square smoke remain. CL water errors are not proof of smoke's root cause.

At live HEAD, scripts/t3_audit_exported_material_programs.py classifies a local shader by the .meta GUID and Material PPtr, checks ShaderLab structure via pass_coverage, and counts dummy markers; it does **not** carry the original Particle108/Shader48 source identity through an authenticated export join. A file with a complete program pass is only a structural candidate, not verified original GPU program or correct blend/alpha/sampler/variant. Thus an apparently healthy aggregate cannot close square-smoke provenance. Earlier same-export T3 result CI41939404454 matched 227/227 UV slots for 41 selected Materials, excluding that particular internal UV mismatch, not all external textures.

Recent Actions sampled: T2 run 42161875055 completed success at 2026-11-06 04:20 UTC (unrelated shader candidate). No new T3 native build or equivalent identity join was requested. No shared files modified. This cycle is a **source audit and bounded evidence gap**, not an integrated visual fix.

## Decisive next action

Coordinate with T3 chat/T5 before shared native workflow edit. In a private SHA-pinned, same-export bounded run, map original Particle108 Shader48 source identity to its actual exported ShaderImporter GUID, then resolve post-restorer Material PPtrs and shader program variants. Require unique identity and exact source pin, capture only sanitized aggregate: matched target count, dummy marker, complete pass count, variant/semantic correspondence, and missing external Texture2D references. If ambiguous, fail closed; never infer original from a name or GUID alone. Only then propose a targeted ShaderLab/texture repair and test Android pixels.

No game assets, .meta, audio, Settings, mouse, Resolution, or CI requests changed. NOT_READY.
