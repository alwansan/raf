# T3 scheduled — smoke pass-factor evidence gap

- session_id: 20261109T1131Z-T3-scheduled-smoke-evidence-gap-p9v4
- origin: scheduled
- branch: feature/android-native-port
- observed HEAD before work: 4ad84778c6d51e24e67d042233e2937672b8e4ba
- registered work commit: 6d42e72ef786f9c54f19624d4d1b43f5e58fae8a
- track: RENDER-002 / NOT_READY

## Read and restored
Owner device report: world entry, save, exit and re-entry worked on artifact 42058825739; delivery publishing failed. Four CL images evidence white hand/raft and square smoke. Owner's later 8 Nov mini-lab requirement supersedes older lab assumptions. Read T3 state/MEMORY and latest scheduled smoke-gate sessions, plus owner requirements and T_TEAM protocol. GitHub branch HEAD above. Recent Actions 42607763178 (T2 foam) completed success; not T3 smoke proof. T3 state.json remains older chat snapshot, not authority for latest scheduled sessions.

## Independent concrete finding
Inspected the current production diagnostic `scripts/t3_smoke_render_state_gate.py`: its FIELDS are exactly `blend_enabled, alpha_test, alpha_blend, program_present`. These booleans do **not** encode SrcBlend/DstBlend factors, BlendOp, per-pass state, ZWrite, Cull, ColorMask, particle texture alpha, material keywords, or sampler binding. Consequently a hypothetical `SCOPED_STATE_MATCH` cannot establish equivalent actual smoke rendering, even with 17 renderer / 34 slot identity checks. This is a static source-contract finding, **not** original shader extraction, not pixel evidence, and not a game fix. The prior 108-use dummy evidence must not be attributed to the distinct 34-use smoke shader.

## Coordination and constraints
Work registered in `prompt/coordination/work/RENDER-002/T3-20261109T1131Z-T3-scheduled-smoke-evidence-gap-p9v4.json` before any resource modification. No other agent's source file changed. No CI launched; no Unity or shared resource. Container GitHub DNS resolution failed (`Could not resolve host: github.com`); connector can read text but cannot fetch original binary source. Did not alter game assets, .meta/GUID, .rgd, audio, Settings, mouse, touch, or package.

## Next exact experiment
1. Obtain pinned original smoke-linked Shader48 source from authenticated ZIP2 in an isolated CI job **only after checking concurrent workflows**; export only sanitized pass metadata and SHA, not proprietary shader text.
2. Record original-to-export per-pass Blend Src/Dst/Op, ZWrite, Cull, ColorMask, shader keywords, texture alpha availability, material render queue and particle renderer mode; distinguish unknown from false.
3. Compare same shader identity and same export instance with phone smoke image and CL logs. Only modify shader/material when a measured mismatch identifies a repair.

Result: OPEN / NOT_READY; evidence-gap documented; no claimed smoke repair.
