# T3 — authenticated Texture2D semantic normal-map parity (5 November 2026)

## Conclusion: 106/106 selected original Texture2D images preserved by the same AssetRipper export **after exact normal-map unpacking**

This is **source/AssetRipper CPU image evidence only**. It is not an Android/Unity ShaderLab rendered pixel, sRGB-equivalence, water FFT, entire-game, new APK, or playable world claim.

The original game ZIP2 source is immutable commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. 11 serialized source providers and three originally streamed image providers were authenticated individually by expected length/SHA before a bounded private actual source export. Original PixelStream files (ZIP2 manifest pins):

| Original stream payload | Bytes | SHA256 |
|---|---:|---|
| `sharedassets0.assets.resS` | 1,779,131,136 | `9169e628e6e7c6fcadfc20e8eae92218f9edbb33c573f6cc474f532437b50ff8` |
| `sharedassets1.assets.resS` | 388,054,288 | `730c91dc3c9d23cc3053d5a8cd8fdb91f09635b96fa5d413e85dbb863b77b2da` |
| `sharedassets6.assets.resS` | 95,361,248 | `5fa2b99646a50762bef980fe4d3dcbba165e7a70aa9fbc4e710a5a9043c67995` |

Total selected external original pixel bytes: **2,262,546,672**. Game bytes/PNG, decoded arrays and private trace GUID/pathIDs were staged only in the disposable runner and **never** uploaded. SHA-pinned public decoder/exporter implementation: `nowl-it/AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8`.

### Authentic source/actual-export evidence chain

1. [CI41942377246](https://github.com/alwansan/raf/actions/runs/41942377246): original 41 Material records, 227 TexEnv/UV fields, 114 exact non-null original→same-export Texture PPtrs (89 same-owner + 25 cross-owner), 113 legitimate nulls; zero missing or wrong target; source-only external ownership 22 sharedassets0 + 3 sharedassets1.
2. [CI41945642710](https://github.com/alwansan/raf/actions/runs/41945642710): **106/106 distinct source-linked Texture2D** require external `.resS` and no original pixel payload was staged in earlier small AssetRipper tests. With only serialized headers, 106 linked export GUIDs had no image importer; this was a **bounded experiment input omission**, not proof of a native project defect.
3. [CI41968665857](https://github.com/alwansan/raf/actions/runs/41968665857): after staging and SHA-authenticating all three genuine `.resS`, 106 selected Texture2D GUIDs all resolved to real PNG/`TextureImporter`; all six sampler fields for 106 linked textures matched, zero unknown overrides. Raw UnityPy original RGBA versus actual PNG: **76 exact and 30 RGB+Alpha drift**, zero missing, wrong dimension, orientation, unsupported or unverified original identities. Its fail-closed exit code 2 was from the deliberately strict *raw* image comparator.
4. [CI42012169446](https://github.com/alwansan/raf/actions/runs/42012169446): new typed original `m_TextureFormat` + `m_ColorSpace` diagnostics prove all **30/30 RAW RGB drifts are Gamma + DXT5**, while **76/76 Linear** textures and all **34 DXT1** are already exact. Original 72 DXT5 = 42 exact +30 raw drift. All 30 raw drifts change alpha and large RGB values, so Gamma/DXT5 *classification alone* did not justify replacing/recoloring game textures.
5. [CI42013419416](https://github.com/alwansan/raf/actions/runs/42013419416): fresh, small original-only SHAs verified for exactly three `.assets` owners (without the 2.26GB `.resS`), actual `m_LightmapFormat` typed census: **every one of the 30 Gamma/DXT5 original objects has original `TextureUsageMode.NormalmapDXT5nm=3`**, and none of 76 other selected original textures has this usage.
6. Exact pinned public AssetRipper `TextureConverter.TryConvertToBitmap(ITexture2D)` branch deliberately calls `UnpackNormal(bitmap.Bits)` when usage is `NormalmapDXT5nm`. In BGRA bytes this copies original packed alpha→red, original red→alpha, keeps green and computes blue normal Z from alpha/green with a clamped square root and C# byte truncation. This **intentionally changes raw PNG RGB+alpha**. It must not be removed merely to make raw-byte equality pass.
7. [**CI42014733420](https://github.com/alwansan/raf/actions/runs/42014733420)**: added a deterministic, non-mutating pure Python equivalent of that exact SHA-pinned C# UnpackNormal formula in `scripts/t3_normalmap_dxt5_semantic.py`, ran it in-memory on **only the 30 authenticated usage=3** original decoded images and compared to their actual SAME-instance PNG using exact GUIDs:
   - RAW baseline remains visible: **76 EXACT + 30 RGB_DRIFT**.
   - Of those original 30 normalmap images, **30/30 exact after upstream-equivalent UnpackNormal**.
   - Other 76 are unchanged and remain exact.
   - **SEMANTIC RGBA 106/106 EXACT**, 0 remaining differences, no pixel normalization/save to repo or export asset edits.
   - 106/106 exporter GUID/`.meta` target match and 106/106 6-field TextureImporter sampler results remain exact.
   - Run finished **SUCCESS**, job output and artifact `t3-original-resS-source-image-export-census-42014733420` contain only aggregate, no raw assets.
   - Synthetic controls for original typed metadata, input image identity, RGBA/BGRA order, reconstructed normal Z sqrt/clamp/`byte` truncation, unused packed B, wrong source format/color/usage, and exception boundaries passed [CI42014621926](https://github.com/alwansan/raf/actions/runs/42014621926).

**Reject** the hypothesis that these 30 original-linked source image values were corrupted by AssetRipper on import/export: the 30 raw RGBA differences exactly implement the declared original normal-map conversion. Do not disable texture gamma/normal imports or generate fake white/albedo textures based on these mismatches. This proof is limited to **106 Texture2D objects truly referenced by the selected 41 Materials**. It does not prove all 7+GB game assets, correct compiled shaders/variants, gamma mapping after Unity import, or the actual Poco/Adreno-rendered scene. `RENDER-002` remains OPEN and overall **NOT_READY**.

## Source and verification

- `scripts/t3_normalmap_dxt5_semantic.py` — C# BGRA→PIL RGBA exact transform in memory only; reject malformed dimensions/modes, wrong original codec/usage/color space.
- `scripts/t3_authentic_decoded_pixel_export.py` — retains original strict raw 76/30 evidence and exposes separate `--verify-normalmap-semantic` **opt-in**: all 106 must match after exact original source mode=3 transform; otherwise still exit 2. Pixel diagnostics format/color-space groups remain aggregate.
- `tests/test_t3_normalmap_dxt5_semantic.py`, `tests/test_t3_pixel_diagnostic_boundary.py` — synthetic format/codec, exact byte lane/math, nonmutation, source identity and decoder-error fail-closed.
- `.github/workflows/raft-t3-decoded-pixel-controls.yml` isolated synthetic controls; `.github/workflows/raft-t3-streamed-original-texture-export.yml` real 11+3 SHA-pinned ZIP2/AssetRipper same-instance 45m private export with safe aggregate only; no Git LFS/Android Unity build or job cancellation.
- Pinned upstream normal branch: `https://github.com/nowl-it/AssetRipperCLI/blob/036098ab525a3f9f693dc101edeb21faad4d32d8/Source/AssetRipper.Export.Modules.Textures/TextureConverter.cs`; original usage enum: `NormalmapDXT5nm=3` in Unity's public TextureImporterEnums.

## Next actionable boundary

T3 source/same-export selected Material tint, UV, Texture GUID, sampler, and decoded texture pixels (with proper normals) no longer demonstrate corruption. Move to **original Shader PPtr → exported Shader GUID identity, actual ShaderLab pass/subprogram/keywords and shader-based GPU color-space/lighting behavior** and ultimately a controlled Unity/Adreno device render from a newly built APK. Coordinate with T1/T2 water/FFT and T5 assets/build, preserve user-confirmed sound/Settings and deferred touch; do **not** label a source-equivalence test as a phone fix.
