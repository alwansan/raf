# T3 scheduled — render-state evidence classifier

- session_id: 20261110T0633Z-T3-scheduled-known-mismatch-g8p2
- origin: scheduled
- resumed_from_sessions: 20261110T0527Z-T3-scheduled-render-state-diff-p7q4; 20261110T0426Z-T3-scheduled-provenance-coverage-a9f2
- base_sha: 0fae32d690f54b2a438d25ab1b807e3e782bca42
- issue_id: RENDER-002 (OPEN; NOT_READY 0/3)
- work: prompt/coordination/work/RENDER-002/20261110T0633Z-T3-scheduled-known-mismatch-g8p2.json

## Verified engineering result
The existing comparator reported INCONCLUSIVE when any field was unknown, even if a different, known field had a definite mismatch; it also listed unknown-vs-known as a confirmed change. The corrected precedence is **MISMATCH if any fully-known field differs; else INCONCLUSIVE if any field unknown; else MATCH**. `changed_fields` excludes unknowns, which remain separately visible in `unknown_fields`. Three regression cases added. Five isolated algorithm checks executed locally and passed; **full repository test suite not yet executed**. Commits: 6a0a064f27645195ae1bb06d8ddb56003dbbf594 (source), e8bc2a21a962523052962ea7c2a380f8ddea85a3 (tests).

## Authenticity and scope
Read owner phone feedback for artifact 42058825739 and T_TEAM owner requirements. Original Material/Texture parity inherited from run 41939404454 is bounded to 41 selected Materials, 227 TexEnv and 89 internal pointers; it does not prove pixel colors or shaders. Prior Smoke34 source provenance remains unresolved. No private assets, .meta, GUID, .rgd, shaders, Settings, audio, mouse, resolution or touch were changed. No Unity/Android run or device test performed. Latest observed HEAD at start 0fae32d690f54b2a438d25ab1b807e3e782bca42; latest sampled Actions included T4 42763994149 success. No duplicate CI dispatched.

## Next action
Run `python -m unittest tests.test_t3_render_state_pair_diff` in repository CI or a checked-out tree, then feed *authenticated* original/export summaries of the same Particle Renderer/material instance to the comparator. Only a measured render-state difference can justify changing ShaderLab Blend/Alpha. Cross-check phone screenshots and CL logs. Keep RENDER-002 OPEN until actual source/export and device evidence.
