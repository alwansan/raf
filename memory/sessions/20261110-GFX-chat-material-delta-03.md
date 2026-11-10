# GFX-LAB — 20261110-GFX-chat-material-delta-03
- session_id: 20261110-GFX-chat-material-delta-03; origin=chat; resumed_from=20261110-GFX-chat-nameindices-02
- base_sha: 7e15a86024491b08e7ede9967d940783f0a92cb0
- source SHA: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- status: SUCCESS_SOURCE_EVIDENCE_NOT_CLOSED

## Why
- 16 owner screenshots/13 logs: six original meshes and Standard fallback colors shown on Adreno, not original Shader48.
- GFX030S CI42753634633: 176 tests, no direct Cull/ZTest/AlphaToMask name bridge and only 2/7 ZWrite, source remains blocked.
- Builder source currently uses sRGBTexture only for basecolor, while the original Metallic Texture2D source metadata is sRGB. Builder hardcodes the Standard glossiness as 0.45, source value unverified.

## Test
- Audit exact seven original Material Renderer slots and linked Metallic Texture2D, quantify the source equality to the fallback 0.45 and sRGB mismatch without exporting private property values/IDs/pixels. Compare only original provenance, not shader pixel parity.
- Persist results in session, STATE/MEMORY/RESTORE/OPEN_WORK; do not create agent or new game APK.


## GFX-OWNER-002 completed
- [CI42754132240](https://github.com/alwansan/raf/actions/runs/42754132240) **SUCCESS 179 tests**, safe artifact [13735385028](https://github.com/alwansan/raf/actions/runs/42754132240/artifacts/13735385028), expiry 2026-11-17T04:11:15Z. SHA-pinned ZIP2 original materials/Texture2D checked privately and source purged.
- Across all seven original Renderer Material slots (112 Float stored entries), original `_Glossiness` **present in 7/7 and equals the Standard test fallback hardcoded 0.45 in 0/7**. Thus the current PBR Standard laboratory mode does not preserve the recorded source Glossiness.
- `_GlossMapScale=1`, `_BumpScale=1`, `_Metallic=0` for all 7 saved-property slots. These are source values, not independently verified Shader48 GPU-interpretation semantics. Raw source Float values beyond fixed diagnostic comparisons were not published.
- Original Metallic Texture2D has sRGB code=1 in 7/7 links, while current Unity Standard importer assigns sRGB only for BaseColor; **7/7 original-vs-fallback Metallic color-space setting mismatch**. BaseColor 0/7 and Normal 0/7 mismatches. Do **NOT** blindly force Standard metallic gamma as an original Shader48 fix; sample data may have custom semantics.
- OriginalShaderRestored=false, GPU/PC pixel parity=false, full item family phase CLOSED=false. Next: actual Shader48 material/register and pass-state bridge, then new true shader GLES3 compile/GPU reference before any worker handoff.
