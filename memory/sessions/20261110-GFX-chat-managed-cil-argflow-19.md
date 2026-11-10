# GFX-LAB 20261110-GFX-chat-managed-cil-argflow-19
- session_id: `20261110-GFX-chat-managed-cil-argflow-19` | origin: `chat` | resumed_from: `20261110-GFX-chat-managed-cil-calls-18`
- base_sha: `e5642fb2d968d002aed0e81ac31e1f2ff55ce736`
- experiment_key: `GFX-MULTI-045`; issue_id: `RENDER-002`
- scope: only `experiment/android-graphics-rootcause`, authentic source-private managed CIL script argument flow; T1–T5 and main/zip2 read-only
- source_ref: original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- Prior verified run: [GFX-MULTI-044 CI42830910833](https://github.com/alwansan/raf/actions/runs/42830910833) SUCCESS, 285 tests, 14 co-presence methods; not true argument flow.
## Hypothesis / control
A forward 12-instruction adjacency can be false. Parse authentic MemberRef method signatures, keep only branch-free and fully-interpreted IL methods, and check that the *first actual Set* call argument* comes from source `ldstr` or a proven `Shader.PropertyToID` transform. Negative controls: wrong overload/argument, unrelated literal, branch, unknown opcode, bad signature, underflow.
## Files / CI
- `gfxlab/tools/multi_shader_managed_cil_argflow.py`
- `gfxlab/tests/test_multi_shader_managed_cil_argflow.py`
- `.github/workflows/gfxlab-multi045-original-cil-argflow.yml`
- CI: pending after commit; actual success/failure and purge must be checked before declaring proof.
## Limits
Even exact script-side Set* arguments do not map Shader48 properties to source DXBC t#/s#/b#/CB byte offsets, do not restore original GLES shader, and do not prove Windows/Adreno pixel parity. No proprietary IL strings, tokens or bytes in public report. `originalShaderRestored=false`, `phase_closed=false`.

## Final verified evidence — replaces pending note above
- CI [42833852638](https://github.com/alwansan/raf/actions/runs/42833852638) success; 295 Python tests, private source SHA pinned, private source purge PASS
- Counts: MethodDefs 19118 / IL 491490 / parse failures 0; property literal methods 17; strict accepted 6 / fail-closed 11; **1 proven Set* first-argument call, 1 original bound texture property passed directly, 0 proven PropertyToID paths** in accepted subset
- Artifact [13773055986](https://github.com/alwansan/raf/actions/runs/42833852638/artifacts/13773055986), expiry 2026-11-17T14:25:56Z
- Positive evidence: source-level script API argument flow, not GPU register or runtime Shader48. Negative controls reject ambiguity. The rejected 11 methods are UNKNOWN, not negative matches.
- outcome: SUCCESS_SOURCE_SCRIPT_ARGUMENT_ONE_ONLY; evidence_level: ORIGINAL_SOURCE_SCRIPT_ARGUMENT_ONLY
- originalShaderRestored=false, real original Material-to-register/CB offset mapping=false, PC/GPU parity=false, G7–G12 blocked
- Next: authoritative original Shader48 reflected resource registers and CB byte offsets / original Windows PC reference capture, preserving private source and branch boundary.
