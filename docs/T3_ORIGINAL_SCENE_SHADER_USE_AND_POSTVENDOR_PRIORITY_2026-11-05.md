# T3 — original scene Renderer→Material→Shader48 use-weight and vendor restoration status (2026-11-05)

**Worker:** T3. **Issue:** RENDER-002 (OPEN). **Scope:** SHA-pinned six real original PC Raft scenes, not 40 scenes, player camera, draw calls, Unity Android shader compilation, Adreno pixels or APK.

## Why these are different measurements

[The genuine 12-owner bounded vendor restoration](T3_BOUNDED_POSTVENDOR_MATERIAL_SHADER_2026-11-05.md) verified that official TMP 3.0.6, PostFX v1 and Volumetric replacements reduce custom **Material document** references to AssetRipper `//DummyShaderTextExporter` from 511 to 495 (54→50 distinct dummy-linked GUID targets). That observation does not rank original **Renderer material slots** or GPU importance. A shader referenced by one Material asset may be assigned to thousands of Renderers, while a shader referenced by many saved Material documents may barely appear in the selected scene.

T3 scheduled session `20261105T132841Z-T3-scheduled-6e9a` correctly added privacy-safe material-*document* frequency bands. This chat session uses different files, source questions and private authenticated identity joins. It preserves both original B03 and scheduled T3 evidence.

## True original six-scene source result

[CI42042819113](https://github.com/alwansan/raf/actions/runs/42042819113) **SUCCESS**. Input ZIP2 git revision `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; `Raft_Data/level0..level5` were each checked against B21 original size/SHA256 pins and four serialized Shader/Material owner files against `SHADER_OWNERS` size/SHA256 pins. The authenticated four-owner staging total is 269,007,288 bytes. No Git LFS, no Windows game binary, no source asset/ShaderLab update, no Unity Editor/Adreno.

Actual original graph was traversed strictly by **per-scene one-based external `m_FileID`**, then the referenced serialized source **Material class21** object, then that Material's separately indexed original **`m_Shader` pointer**, then the source **Shader class48** identity/parsed Pass structure. Unknown original owner identities were classified as unverified, not guessed from exported GUIDs or names.

| Original six-scene metric | SHA-pinned result |
|---|---:|
| Renderer objects with Material-slot records | 1,495 |
| Material slots | 1,639 |
| True original null Material slots | 4 |
| Non-null original Material slots resolving to Material class21 | **1,635** |
| Distinct Material source objects used by these Renderers | **120** |
| Distinct original Shader pointer objects referenced | 22 |
| Material slots resolving to typed original Shader48 within four pinned owners | **1,633** |
| Distinct typed Shader48 objects in those 1,633 slots | **21** |
| Material slots to one other original Shader owner not staged for class check | **2** |
| Source Renderer Material slots referencing verified Shader48 with >1 original serialized Pass | **1,418** |

The 21 typed original Shader48 targets are all from `sharedassets0.assets`; the remaining 2 slots target a single original owner `globalgamemanagers.assets` outside this four-owner typed Shader scope. No unknown source type is labeled missing/corrupted. No original Material Shader pointer was null in this selected Renderer scope.

### Shader use is highly concentrated

The sorted original Renderer **Material-slot use counts** for the ten most frequently referenced Shader objects, with no source object IDs/GUIDs/names disclosed, are:

`[921, 219, 121, 108, 70, 34, 34, 30, 20, 16]`.

The highest-usage Shader is assigned to **921 of 1,635 non-null original Material slots**, approximately 56.3%, and the highest four source Shader objects account for **1,369 of 1,635 slots**. These are **slot counts**, not unique visible mesh counts, draw calls, shader execution times or device pixels.

Verified source-defined Shader material-slot frequency bands across 22 distinct referenced Shader pointers: `1 use: 4 shader targets`, `2–4 uses: 3 targets`, `5–16 uses: 6 targets`, and `17+ uses: 9 targets`. Renderer-distinct frequency is tracked separately to avoid double-counting multiple slots on a Renderer.

## Separate true same-instance export-to-postvendor join

Independent follow-up workflow `.github/workflows/raft-t3-scene-renderer-shader-postvendor-join.yml` reuses an actual SHA-pinned 12-provider B21/W1/B02 AssetRipper original export, verifies the same-instance original Material↔Shader48 source pointer lineage, applies authentic TMP/PostFX/Volumetric vendors in disposable output, and joins **original source Shader48 ID → W1 actual Shader GUID → real `.shader/.shader.meta` program marker**, all in private runner RAM. It will classify the source 921-slot high-usage shader as *still Dummy*, *non-Dummy after vendor restoration* or *Unity engine builtin*.

This is a distinct falsifiable source→postvendor question, not proof that an Android APK has already been visually repaired or that default-Dummy 495 Material documents correspond one-for-one to original Renderers. The vendor restorer phase excludes full native builtins/Depth/Blur/FFT, Unity Android import and device results. All original source bytes, private trace IDs and ShaderLab files remain confined to the runner; only safe aggregate numeric bands are published.

## Engineering next action

Use the authenticated same-instance join result to prioritize **high original Renderer-slot-use Shader48 programs that still carry Dummy fallback after vendor restoration**. Only real source compiled stages, variants, SubShader/Pass state and Unity-compatible restoration under existing GUIDs are acceptable. Do not insert synthetic Passes, rewrite Material colors whose authentic RGBA/UV are already proven, or treat a compiled-looking CGPROGRAM as original shader fidelity. Coordinate full native import/phone visual feedback with T5 and water FFT T1/T2. Keep working sound/Settings stable, touch and layout development deferred.

**Status:** RENDER-002 OPEN. No game asset, `.shader`, `.meta`, APK, OBB, XAPK, phone build or audio/Settings/touch changes by this chat session.
