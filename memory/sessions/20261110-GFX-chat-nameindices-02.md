# GFX-LAB — 20261110-GFX-chat-nameindices-02
- session_id: `20261110-GFX-chat-nameindices-02`
- origin: chat
- resumed_from: `20261110-GFX-chat-owner-evidence-01`
- base_sha: `3fe1f4a1b36f665cf64bc654f3af5260e1983fbf`
- source_ref: `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- experiment_key: GFX-MULTI-030S exact Shader48 dynamic PassState ↔ same-pass NameIndices/ShaderProp/MaterialKeywords
- evidence baseline: [GFX-MULTI-029S CI42750996280](https://github.com/alwansan/raf/actions/runs/42750996280) 164 tests, ZWrite 2/7 matches with Float slots; Cull/ZTest/AlphaToMask 0/7 direct property matches. [GFX-MULTI-013 CI42732808109](https://github.com/alwansan/raf/actions/runs/42732808109) 7/7 source pairs GLSL offline only. [Owner GFX026 review](../sessions/20261110-GFX-chat-owner-evidence-01.md) shows Shader48 NOT running on phone.
- scope: source-only 7 Shader48 Passes, m_NameIndices and same-source metadata; compare original named state values without emitting strings/IDs/compiled shaders. Fail closed on unknown structures, no numeric fallback.
- status: SUCCESS_SOURCE_EXACT_NAMEINDICES_NEGATIVE_GATE
- next: analyze CI, update memory and phase closure gates; do NOT claim original Android Shader48 until material/source→GL/PC pixels pass.


## GFX-MULTI-030S completed
- [CI42753634633](https://github.com/alwansan/raf/actions/runs/42753634633) **SUCCESS 176 tests**. Safe aggregate artifact [13734278874](https://github.com/alwansan/raf/actions/runs/42753634633/artifacts/13734278874), expiry 2026-11-17T04:07:10Z. ZIP2 original staged privately and purged.
- Source original Shader48 six models/7 Material slots/2 SubShaders/7 Passes. Source `m_NameIndices` metadata **present with string tokens in 7/7** Passes, yet **0/7 direct exact string matches** against each of culling, zTest, alphaToMask and zWrite. Original material `m_ValidKeywords` matches also 0/7 for each.
- Source Shader48 property/Material Float direct matching: Cull 0/7, ZTest 0/7, AlphaToMask 0/7; **ZWrite 2/7 original Shader property matches, 14 renderer-slot value matches** (2×7), remaining 5/7 unmatched. **No interpolation of numeric hashes/array order**.
- Definitive evidence scope: `PASS_STATE_DYNAMIC_OVERRIDE_DIRECT_SOURCE_BRIDGE_BLOCKED` in 26 of 28 field×pass cases; ZWrite 2/7 partial. This is not full shader meaning and not proof no other source/compiled metadata can bridge. No GLES3 ShaderLab original or PC parity; phase CLOSED=false.
