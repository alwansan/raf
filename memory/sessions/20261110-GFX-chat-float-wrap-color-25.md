# GFX-LAB — 20261110-GFX-chat-float-wrap-color-25

- session_id: `20261110-GFX-chat-float-wrap-color-25`
- origin: `chat`
- resumed_from: `20261110-GFX-chat-material-texture-semantics-24`
- base_sha: `904f314b00de490a39e5278b5b608087c0bd46cb`
- source_ref: `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- experiment_key: `GFX-MULTI-024-material-float-color-wrap-format-census`
- scope: Seven exact original Materials (112 floats, 14 colors) and 21 bound Texture2D serialized settings, properties cross-referenced privately to one authentic Shader48 (27 properties), official Unity 2021.3 enums; no pixel decode, no Android APK.
- workflow: `.github/workflows/gfxlab-multi-material-float-wrap.yml`
- status: `SUCCESS_SOURCE_ONLY_GFX_MULTI_024`

## Baseline and controls

- Source evidence: [GFX-MULTI-023 CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) SUCCESS, 21/21 original textures decoded and SHA-authenticated; material tint 7/7 white and all 21 UV identity.
- Prior shader reflection coverage: [GFX-MULTI-022 CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) SUCCESS, 1,435 linked variant rows and 1,275 unique DXBC stage programs have no RDEF/serialized parameter tables. Property → t/s registers still UNKNOWN.
- Unity 2021.3 C# reference pinned branch commit `b052b1fe38b45d5aefa609a115c626ed2e74f3a6`: [GraphicsEnums.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs) documents TextureFormat DXT1=10, DXT5=12; internal TextureColorSpace Linear=0, sRGB=1; FilterMode Bilinear=1; TextureWrapMode Repeat=0, Clamp=1, Mirror=2, MirrorOnce=3.
- TextureColorSpace is an **internal texture enum**, not PlayerSettings.ColorSpace; code treats missing fields as unknown, not default values.
- All raw asset names, material values, shader names, PPtrs, GUIDs, texture bytes/pixels remain inside the ephemeral runner.
- CI is original source-only; no original Shader48 restored, no Adreno/PC pixel parity, no animation/rig or water/FFT claims.

## Next required report

- Verify original source ZIP2 owner SHA and six selected model identity.
- Test 112 floats and 14 colors for source name membership, scalar value buckets, and safe named categories.
- Inspect 21 Texture2D m_TextureSettings.WrapU/V/W, FilterMode, Aniso, MipBias, plus TextureFormat/TextureColorSpace/mip counts.
- Record run success/failure and private data purge, then update this session, RESTORE, OPEN_WORK_AND_IDEAS, MEMORY, STATE. If a source-field mismatch is found, report it rather than silently substituting a default.

## GFX-MULTI-024 — verified result (2026-11-10)

- [CI42745345599](https://github.com/alwansan/raf/actions/runs/42745345599) FAILED after 139 unit tests: an incorrect uniqueness guard assumed seven material slots meant seven distinct Material21 assets. Source purge succeeded.
- Fixed to distinguish slot references from unique identities. [CI42745536309](https://github.com/alwansan/raf/actions/runs/42745536309) COMPLETED SUCCESS: 139 unit tests; original SHA-pinned ZIP2 source; six models, **7 renderer material slots / 6 distinct Materials**, **21 Texture2D links / 18 distinct images**. Runner private source purge succeeded.
- Original saved properties: **112/112 Float labels and 14/14 Color labels match Shader48's 27-property declaration**; this does NOT establish any property-to-register binding/CB byte offset. Seven slots have white RGBA tint; seven other saved color slots are nonidentity (unknown semantics).
- Float buckets: zero 33, one 58, strictly between 0 and 1: 21. Safe name categories: alpha-cutout 7, blend 14, depth 7, gloss 21, height 7, metallic 7, normal-strength 14, occlusion 7, render-mode 7, UV channel 7, unclassified 14. No raw names/values exported.
- Original TextureFormat: BaseColor DXT1×5 + DXT5×2; Normal DXT5×7; Metallic DXT5×7. Original internal TextureColorSpace: BaseColor sRGB×7, Normal Linear×7, Metallic sRGB×7. WrapU/V/W Repeat each 21/21, FilterMode Bilinear 21/21, Aniso=1 and MipBias=0 on all 21 original image links.
- Official Unity 2021.3 enum grounding: [UnityCsReference GraphicsEnums.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs) @ branch HEAD b052b1fe38b45d5aefa609a115c626ed2e74f3a6. Internal TextureColorSpace != PlayerSettings.ColorSpace.
- [Safe aggregate artifact 13730024662](https://github.com/alwansan/raf/actions/runs/42745536309/artifacts/13730024662), expires 2026-11-17T02:51:51Z UTC. No raw source Shader/ID/name/value, image, GPU pixel, APK, OBB, or third-party branch changes.
- Evidence level ORIGINAL_SOURCE. OriginalShaderRestored=false; original property→DX11 register mapping=false; Android GPU/PC pixel parity=false; rig/animation, water/FFT, smoke/fire still OPEN.

## Next: GFX-MULTI-025
Identify seven nonidentity second Color slots by exact shader property-name semantics without publishing original names/values; separately census shared Material21 / Texture2D identities across M00–M05. Do not infer emissive GPU behavior or convert Metallic sRGB to Linear without a controlled device/PC reference. Do not create an agent or game APK.
