# GFX-LAB — 20261110-GFX-chat-original-shader-text-source-22
- session_id: 20261110-GFX-chat-original-shader-text-source-22; origin: chat
- resumed_from: 20261110-GFX-chat-original-material-texenv-21
- base_sha: 090993480abe7b4fc3f541b03357f71fa3fc1a77
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-021-source-Shader48-embedded-script-evidence-and-material-property-name-identity
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: check original typed Shader48 embedded m_Script/HLSL text evidence and source 27 serialized shader properties against seven original Material TexEnv lists (63 slots/21 bound). All source property names/script bytes remain in private runner and never exported.
- previous: GFX-MULTI-020 [CI42740776655](https://github.com/alwansan/raf/actions/runs/42740776655) SUCCESS 103 tests; selected 14 source Shader48 player program rows had 0 m_Parameters, 7 original materials contain 21 actually bound Texture2D and 42 null TextEnv slots; no original name-to-t register mapping. This confirms earlier GFX-MULTI-006 param_metadata_variants zero.
- negative_controls: marker presence alone not proof of material-to-register mapping, require real script field, bound original TexEnv subset, original Shader48 and SHA identity, never output source strings.
- planned_run: GFX-MULTI-021 workflow on commit (CI_PENDING).
- evidence_level: ORIGINAL_SOURCE MATERIAL PROPERTY LIST and EMBEDDED TEXT CHECK only. Original Shader48 Android renderer/PC pixels/CB layout FALSE.
- next_step: after CI, update current session/restore/MEMORY/STATE/open work. If original embedded source absent, mark property->register mapping BLOCKED, maintain separate material/texture validation and propose same-export/manual PC reference for shader semantic proof.

## GFX-MULTI-021 final source result and negative controls
- [GFX-MULTI-021 CI42741817991](https://github.com/alwansan/raf/actions/runs/42741817991) **COMPLETED SUCCESS**, 107 source-free tests, genuine fixed ZIP2 source Shader48/Material21 inside ephemeral runner.
- Original Shader48: 27 serialized Shader properties, including 9 Texture-type properties. Seven actual original Material slots: 63/63 stored `m_TexEnvs` property names occur in Shader48 properties. Of these, 21/21 actually bound Texture2D property names occur in Shader48 declarations: precisely **7 basecolor + 7 normal + 7 metallic** original bound roles; 42 originally null TexEnv entries preserved.
- Shader48 typed object **does not expose embedded `m_Script` field**, `embedded_script_bytes=0`, HLSL/CGPROGRAM markers false, source `register(t#/s#)` markers false.
- Taken together with GFX-MULTI-020 [CI42740776655](https://github.com/alwansan/raf/actions/runs/42740776655) (0/14 selected source program `m_Parameters`) and GFX-MULTI-015 [CI42736017218](https://github.com/alwansan/raf/actions/runs/42736017218) (RDEF absent 14/14 representative stages), **no authoritative Material property name → original DX11 t#/s# register mapping** is currently available from these selected serialized source fields.
- This does NOT prove all 524 matched stage variant pairs are stripped; original shader variants elsewhere may hold missing reflection. It does NOT prove loss of models/textures; the source Material and Shader property relationships are strong ORIGINAL_SOURCE evidence.
- GFX-MULTI-019 [CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) separately mapped 29 original DX11 t# and 27 original s# to SPIR-V descriptor names (56/56) but cannot associate the material property name to t/s without further source evidence. Do not guess material property order or announce Android Shader48 restored.
- Private original script fields/material names/paths removed from CI runner; no device GPU proof or pixel parity in GFX-MULTI-021.
- Next GFX-MULTI-022: bounded survey of other authentic Shader48 compiled program variants for RDEF/m_Parameters or same-export authoritative shader source/sidecar; if none found, preserve explicit source bridge BLOCKED, perform separate CPU material/tangent/CB tests and request PC reference rather than deploying guessed shader.
