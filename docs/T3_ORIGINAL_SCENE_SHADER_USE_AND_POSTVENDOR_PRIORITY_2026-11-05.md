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

## Authentic source→same-export postvendor outcome

[CI42044249541](https://github.com/alwansan/raf/actions/runs/42044249541) **SUCCESS**, full independent original ZIP2 12-owner authenticated source → real AssetRipper W1 Material21/Shader48 + B02 Texture2D28 private **same-instance** output → original Material pointer proof (41/41) → actual official TMP/PostFX/Volumetric restorers → actual postvendor `.shader/.shader.meta` GUID and program marker. Reused all six original scene source blobs and reverified 1,633 original typed Shader48 slots and 21 source Shader48 identities; no names/IDs/GUIDs/materials/shader source uploaded.

Distinct populations were verified independently in the same process:
- Bounded generated Material YAML documents: **731** total, **511** custom and 220 Unity builtins; **495** still custom Dummy after the three vendors, 50 distinct linked Dummy GUID targets. `.mat` and `.shader.meta` original export bytes preserved by vendor restorers.
- **Original six-scene Renderer material-slot references to 21 exact source Shader48 objects:** **1,633** typed source slots, of which **1,373** point via W1 original Shader48→actual exported Shader GUID to files **still containing `//DummyShaderTextExporter`** after the three vendor restorers, **256** map via actual exporter to Unity builtin Shader GUIDs, and **4** point to a custom non-Dummy vendor-restored program. **2** additional original Renderer Material slots target a Shader owner outside the four typed source-owner set; left UNVERIFIED rather than silently counted as a known output.
- 21 typed source Shader48 targets: **17** still have Dummy output ShaderLab, **3** are Unity-builtin transported output pointers, and **1** has a non-Dummy restored file.
- **The highest-use original source Shader48, referenced by 921 Material slots across the source six scenes, STILL has a real exported `DummyShaderTextExporter` file after three vendor restorers**, not a name-based inferred match. Top use counts for still-Dummy source Shader48 identities (identity withheld) start with `[921, 121, 108, 70, 34, 30, 20, 16, 16, 15]`. The sole vendor non-Dummy Shader48 has four original Renderer Material-slot uses.
- **This is NOT production full-native postrestorer output:** separate verified builtins, Depth Copy, Blur, FFT/water and other native stages were *not* run in this isolated B21 experiment. The actual source→export Renderer material assignment was not checked; the mapping tracks original Renderer→Material→Shader48 source usage to the same Shader48 export GUID and real output ShaderLab. Neither source slot counts nor Dummy marker count proves visible white pixels, draw calls, Unity/Adreno execution or complete shader variant semantics.

The experiment additionally validated the previous 12-owner TMP/PostFX/Volumetric 16 Material-document dummy-link reduction in this newly reconstructed source run; it did not mutate repository game assets or original metadata. The separate real [CI42042819113](https://github.com/alwansan/raf/actions/runs/42042819113) source-only census remains the independent original material-slot baseline.

**Reproduction:** [source-only scanner](../scripts/t3_original_renderer_shader_impact.py), [true postvendor identity bridge](../scripts/t3_source_renderer_shader_to_postvendor_export.py), [adversarial tests](../tests/test_t3_source_renderer_shader_to_postvendor_export.py) and [standalone CI](../.github/workflows/raft-t3-scene-renderer-shader-postvendor-join.yml), all on `feature/android-native-port`, with the original ZIP2 commit and public AssetRipper pinned as in the inherited vendor experiment. Safe numeric-only artifact `t3-6scene-authentic-Shader48-sameexport-postvendor-42044249541` (retention 7 days, artifact id 13423658322).

## Independent original Shader exact-name coverage by authenticated Unity 2021 builtins

[CI42046329453](https://github.com/alwansan/raf/actions/runs/42046329453) **SUCCESS**: rebuilt the **six exact original scene + four source owner** SHA-pinned ZIP2 input and authenticated the official Unity 2021.3.45f2 runtime built-in ShaderLab archive against the pinned SHA256 `5cb0f9c4d022d6054d179778b9b50a0301d6748eaf4abdedd21c93f0c30b10c5` before parsing 198 Shader identity names. Compared **exact serialized original `Shader48.m_ParsedForm.m_Name` strings privately** to the verified vendor archive, never printing original names/IDs/GUIDs, individual hashes, or archive shader source.

- **The original 921 Renderer-slot highest-use Shader48 has NO exact name match in the official Unity 2021 builtin runtime Shader archive.** Thus `scripts.restore_builtin_shaders`'s exact-name source replacement route cannot be assumed to restore that high-use program automatically.
- Exactly **3 of the 21** original typed source Shader48 names match the authenticated Unity builtin archive; they account for exactly **256 original Renderer Material-slot uses** (use counts `219+34+3`). This independently matches the 3 Shader48 objects and 256 source slots that the **same-instance AssetRipper output** redirected to Unity built-in GUIDs in CI42044249541.
- The other **18 original Shader48 source names** represent **1,377 original Renderer material-slot uses** without an archive builtin match; this is the same **1,373 still-Dummy** + **4 vendor non-Dummy** subset in the postvendor identity bridge. This cross-check is source-authentic yet **not a Unity imported program equality or device pixel proof**.

Source helper [`scripts/t3_top_original_shader_builtin_coverage.py`](../scripts/t3_top_original_shader_builtin_coverage.py), adversarial [tests](../tests/test_t3_top_original_shader_builtin_coverage.py), [isolated CI](../.github/workflows/raft-t3-top-renderer-shader-builtin-source-match.yml). Real source code and vendor archive are used solely in ephemeral CI memory; published aggregate safe numeric flags only. Original and game projects are not modified.

## Engineering next action

Use the authenticated same-instance join result to prioritize **high original Renderer-slot-use Shader48 programs that still carry Dummy fallback after vendor restoration**. Only real source compiled stages, variants, SubShader/Pass state and Unity-compatible restoration under existing GUIDs are acceptable. Do not insert synthetic Passes, rewrite Material colors whose authentic RGBA/UV are already proven, or treat a compiled-looking CGPROGRAM as original shader fidelity. Coordinate full native import/phone visual feedback with T5 and water FFT T1/T2. Keep working sound/Settings stable, touch and layout development deferred.

**Status:** RENDER-002 OPEN. No game asset, `.shader`, `.meta`, APK, OBB, XAPK, phone build or audio/Settings/touch changes by this chat session.
