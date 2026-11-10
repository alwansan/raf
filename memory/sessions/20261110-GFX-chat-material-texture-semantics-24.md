# GFX-LAB — 20261110-GFX-chat-material-texture-semantics-24

- session_id: 20261110-GFX-chat-material-texture-semantics-24
- origin: chat
- resumed_from: 20261110-GFX-chat-variant-reflection-sweep-23
- base_sha: 253a2981fc246b810965ece4637a33516382be6e
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-023-original-material-texture-semantic-and-channel-census
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: six models, seven Materials, 63 TexEnv slots, 21 bound Texture2D objects, Material color/float/int slots, UV transforms, Texture2D format/color-space/mip/settings metadata and decoded RGBA channel variability.
- workflow: .github/workflows/gfxlab-multi-material-texture-semantics.yml
- final_workflow_commit: 0eadbc73f97bb8c8524c9cedc5c75d7409cfcb9a

## Runs and evidence

- First attempt [CI42743969290](https://github.com/alwansan/raf/actions/runs/42743969290): source plan succeeded (six models, seven materials, 21 textures, 15 chunks / 707,788,800 bytes). Audit failed because it re-ran `stage_originals` after sparse checkout replaced the checkout patterns and removed `RAFT_FILE_MANIFEST.tsv`. No texture analysis was accepted from that attempt; private purge succeeded.
- Fixed the audit to reuse the already SHA-verified staged owner assets and validate their owner hashes after sparse checkout.
- Final [CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412): **COMPLETED SUCCESS**, 128 tests passed; sparse authenticated hydration, all 21 Texture2D decodes, safe report, artifact upload and private purge all succeeded.
- Artifact [13730562085](https://github.com/alwansan/raf/actions/runs/42744204412/artifacts/13730562085), expires 2026-11-17T02:40:48Z UTC.

## GFX-MULTI-023 results

- Six selected source models; seven Materials; 63 TexEnv entries; 21 bound / 42 null; exact role distribution 7 BaseColor, 7 Normal, 7 Metallic.
- All 21/21 original Texture2D objects decoded with exact dimensions. Total 53,477,376 pixels; 15 authenticated Git chunks / 707,788,800 selected bytes.
- Material saved-property slots: 14 colors, 112 floats, 0 ints. Seven authored tint slots are all identity white (7/7); non-white tints 0. UV scale/offset: identity 21/21; nonidentity 0.
- Raw source texture codes (not semantically interpreted): format BaseColor {10:5,12:2}, Normal {12:7}, Metallic {12:7}; color-space BaseColor {1:7}, Normal {0:7}, Metallic {1:7}; mip-count BaseColor {11:3,12:4}, Normal {11:3,12:4}, Metallic {11:5,12:2}; filter mode code 1 on all 21.
- Texture settings, anisotropy and mip-bias fields present 21/21. Generic `m_WrapMode` not available in current typed tree; inspect WrapU/WrapV/WrapW in GFX024. Do not treat unavailable as false.
- BaseColor channels: R/G/B variable 7/7; Alpha variable 2/7, fully opaque 5/7.
- Normal channels: R constant 7/7; G/B/A variable 7/7; simple A+G / constant R+B conventional DXT5nm candidate 0/7. This does not prove another encoding.
- Metallic channels: Alpha variable 7/7; R/G/B variable 4/7 and constant 3/7. Alpha may carry additional data, but smoothness meaning is unverified.
- Safe report: names, PPtrs, raw pixels, image files and shader/register data exported=false. Runner purge confirmed `GFX_MULTI023_ALL_PRIVATE_SOURCE_AND_TEXTURE_DATA_PURGED=true`.

## Limits

- Texture format and color-space codes are raw serialized codes; authoritative Unity 2021.3 interpretation remains pending.
- Material float slot meanings and TextureSettings wrap axes remain unverified.
- This is ORIGINAL_SOURCE decode evidence, not Unity GLES/Adreno/PC pixel parity. No APK or owner test was performed.
- `originalShaderRestored=false`; `actual_android_original_shader_pixels_verified=false`; `phase_closed=false`. RENDER-002 and WATER-001 remain OPEN.

## Next step

- **GFX-MULTI-024**: private semantic census of the 112 Material float slots and 14 color slots, TextureSettings WrapU/WrapV/WrapW, and authoritative Unity 2021.3 enum interpretation for texture format/color-space codes. Keep names and values private; emit only safe categories/counts. After that, decide whether an Android GPU channel-viewer probe is justified.
