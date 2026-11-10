# GFX-LAB — 20261110-GFX-chat-passstate-material-binding-29
- session_id: 20261110-GFX-chat-passstate-material-binding-29; origin: chat
- resumed_from: 20261110-GFX-chat-renderstate-enum-28
- base_sha: 2972cfce2736c0790db5fb317d201c313c69fdbf
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- experiment_key: GFX-MULTI-029S-original-Shader48-StateNamedParams-to-MaterialSavedFloat
- issue_id: RENDER-002
- scope: original Shader48 seven Passes / 7 Material slots, match source m_State.culling/zWrite/zTest/alphaToMask.name to 27 shader property names and seven signed m_SavedProperties.m_Floats maps, count enum-valid categories; no original property names/values, shaders, textures or GUID/PPtr exported, no Android APK or T-Team changes.
- evidence baseline: [GFX-MULTI-028S CI42749968983](https://github.com/alwansan/raf/actions/runs/42749968983) SUCCESS 159 tests, 7/7 named dynamic states for all four fields, source 7 m_ValidKeywords nonempty; [GFX026 CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) standalone signed diagnostic Android channel APK, not original Shader48, owner device pictures/logs outstanding.
- hypothesis: original dynamic shader pass state names can be linked directly to original Float properties in Material saved tables without guessing numeric fallback.
- negative_controls: exact property name lookup only (allow explicit [_Property] ShaderLab bracket syntax), no array order mapping, invalid Float enum values flagged, missing property means source mapping unavailable. Full GPU Shader48 parity false.
- run: GFX-MULTI-029S auto-trigger on workflow push; CI_PENDING at creation.
- next_step: inspect CI source counts and update RESTORE_AR.md, session, STATE.json, MEMORY.md, OPEN_WORK_AND_IDEAS_AR.md; test device channel APK separately, original shader and PC GPU parity open.

## GFX-MULTI-029S VERIFIED CI42750996280 — original named pass state to Material saved Float diagnostic
- [CI42750996280](https://github.com/alwansan/raf/actions/runs/42750996280) COMPLETED SUCCESS **164 unit tests**. Fixed original ZIP2 source Shader48 7 Passes, 7 source Material21 Renderer slots, 27 original shader property names, no shader/private names/floats/bytes exported. Negative control tests confirm exact direct name match and explicit bracket syntax only; no array order / numeric fallback guesses.
- All seven Passes had parseable `m_State` named parameters for each Cull/ZWrite/ZTest/AlphaToMask. **Culling: 0/7 names in original Shader48 serialized properties; 0 original Material saved Float matches. ZTest: 0/7, 0. AlphaToMask: 0/7, 0.**
- **ZWrite only: 2/7 original Pass names match Shader48 serialized properties; total 14 per-Pass × per-Material-slot float matches** (2 source Pass references ×7 original Renderer Material slots; NOT 14 distinct Material objects). All 14 matching original Float values are allowable 0/1 enum values; no unrecognized values.
- Missing direct serialized property/saved-Float matches do NOT mean other states disabled or the strings invalid. They may be other engine/compiled named state references or absent material/keyword metadata. Do not treat `m_State.val` as effective render state just because there is no saved Float; no Shader48 Android GPU or PC pixel evidence. `m_ValidKeywords` original source remains nonempty 7/7 (GFX028S), but keyword string/register mapping remains open.
- No full-game or APK modification. Original ZIP2 staging purged. GFX-MULTI-026 signed channel APK [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) is separately downloadable, device screenshots and COPY LOG not yet supplied. It is a diagnostic shader, NOT original Shader48.
- Next source-only GFX-MULTI-030S: compare unmatched dynamic pass state names to original per-Pass `m_NameIndices` and any verified same-source metadata, without exposing names or presuming equivalence. If still unresolved, preserve `PASS_STATE_DYNAMIC_OVERRIDE_SOURCE_BLOCKED`; request matched PC reference rather than hardcode states. Independently examine rtBlend/ColorMask and original Material property import semantics.
