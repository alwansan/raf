# GFX-LAB — 20261110-GFX-chat-material-delta-03
- session_id: 20261110-GFX-chat-material-delta-03; origin=chat; resumed_from=20261110-GFX-chat-nameindices-02
- base_sha: 7e15a86024491b08e7ede9967d940783f0a92cb0
- source SHA: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- status: PREPARING

## Why
- 16 owner screenshots/13 logs: six original meshes and Standard fallback colors shown on Adreno, not original Shader48.
- GFX030S CI42753634633: 176 tests, no direct Cull/ZTest/AlphaToMask name bridge and only 2/7 ZWrite, source remains blocked.
- Builder source currently uses sRGBTexture only for basecolor, while the original Metallic Texture2D source metadata is sRGB. Builder hardcodes the Standard glossiness as 0.45, source value unverified.

## Test
- Audit exact seven original Material Renderer slots and linked Metallic Texture2D, quantify the source equality to the fallback 0.45 and sRGB mismatch without exporting private property values/IDs/pixels. Compare only original provenance, not shader pixel parity.
- Persist results in session, STATE/MEMORY/RESTORE/OPEN_WORK; do not create agent or new game APK.
