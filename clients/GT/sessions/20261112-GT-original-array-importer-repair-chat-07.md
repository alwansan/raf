# GT — 2026-11-12 — دورة Chat-07: استعادة import أصل Texture2DArray دون إعادة إنشاء صور اللعبة

- **agent/session_id:** `GT / GT-20261112-CHAT-07-ORIGINAL-ARRAY-IMPORTER`
- **origin:** `chat`
- **branch الوحيد للكتابة:** `feature/android-native-port`
- **source:** original `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`; SHA256 manifest; **NO Git LFS**
- **scope:** 9 original `Texture2DArray` (Unity ClassID187), 28 real Material texture references; avoid T5 native build and T1–T5 files

## Evidence read and actual cause

- [AssetRipper full #43143899920 SUCCESS](https://github.com/alwansan/raf/actions/runs/43143899920): **9/9 actual PNG atlas images already have full rectangular source-layer capacity**, with exact 1024×1024 per original source slice. `PNG_has_all_original_layers_in_cell_grid=9`; `importer_grid_needs_source_verified_correction=9`; all nine `flipbookRows` and `flipbookColumns` missing or nonpositive. In same instance 9 original class187 assets, 28 Material PPtrs use 18700000, unchanged true source GUIDs. Main blocker: **bad TextureImporter flipbook cell grid**, not missing source pixels, texture guid or wrong flattening to Texture2D. Prior ZIP2 original 8 BC3 streams (50 layers) verified and staged 69,906,400 bytes in [43138326757 PASS](https://github.com/alwansan/raf/actions/runs/43138326757). The ninth source array has zero original stream/inline pixels (2 logical layers) and must never have fabricated colors.
- See upstream [Unity 2021.3 TextureImporter flipbookColumns](https://docs.unity.cn/2021.3/Documentation/ScriptReference/TextureImporterSettings-flipbookColumns.html) and [AssetRipper issue #1691](https://github.com/AssetRipper/AssetRipper/issues/1691) about zero-column exported array PNGs. These support the diagnosed failure mode but do not constitute proof of Unity Editor import.
- [GT full #43141107035](https://github.com/alwansan/raf/actions/runs/43141107035) had separate pixel comparison INCONCLUSIVE because it required already-valid importer grids before comparing pixels. Reworked read-only parity script to compare actual PNG atlas cells even while importer metadata invalid; synthetic [43143986147 PASS](https://github.com/alwansan/raf/actions/runs/43143986147); real rerun [43144656957](https://github.com/alwansan/raf/actions/runs/43144656957) was executing at checkpoint.

## Actual code implemented on branch

- `scripts/gt_repair_array_flipbook_importers.py`: SHA-pinned 82 original ZIP2 owner identities + same-instance AssetRipper trace; exact 9 original class187 GUIDs; confirms each *fully decodable valid PNG* holds exactly original depth layers via 1024px cell geometry. If and only if complete, corrects the existing `.png.meta` `flipbookRows/Columns` values **without touching PNG pixels, material pointers or GUID**; retains byte-perfect private backups, fails closed and rolls back on corruption/unrelated .meta mutation. Safely skips incomplete image arrays. Tests incl forged/truncated PNG, wrong GUID, wrong shape, missing layers [43146010385 PASS](https://github.com/alwansan/raf/actions/runs/43146010385).
- `scripts/gt_verify_original_array_material_refs.py`: independent postrepair proof of **all 28 actual Material TexEnv PPtrs** to 9 source original ClassID187 array importers with fileID18700000 and source layer grids. Synthetic negative tests [43145778708 PASS](https://github.com/alwansan/raf/actions/runs/43145778708).
- `scripts/gt_validate_bc3_array_slice_order.py`: independent source-side UnityPy array images vs Pillow BC3 mip/slice decode, distinguishing `slice_major` vs `mip_major`, keeping all pixels private; synthetic [43145331681 PASS](https://github.com/alwansan/raf/actions/runs/43145331681). Based on actual UnityPy Texture2DArray reader, which subdivides image data by `m_DataSize // m_Depth`, but real ZIP2 decoder comparison remains pending at checkpoint.
- `scripts/gt_compare_original_bc3_to_flipbook_pixels.py` now allows first-cell source preview and incomplete importer grid as **diagnostic only**, never proof of full array if only one cell. Full original Atlas pixel parity is separately reported from class/atlas/PNG geometry.
- `.github/workflows/raft-gt-original-export-smoke.yml` triggers actual separate GT real AssetRipper source export → BC3 recovery → original array independent layout check → original PNG atlas pixel comparison → scoped importer meta repair → 28 Material array refs closure → full 82-owner Material TexEnv audit → official vendor Shader restorers. No Android/XAPK or T5 votes altered. Several in-progress/queued full CI runs due non-cancel GT workflow group: [43144656957](https://github.com/alwansan/raf/actions/runs/43144656957), [43145816256](https://github.com/alwansan/raf/actions/runs/43145816256). Read **step-level reports**, not overall GitHub Workflow `success` (some diagnostic steps are continue-on-error).

## Unproven / next

1. Review real CI per-step `GT_REAL_SAFE_TEXTURE2DARRAY_GRID_REPAIR` for **9/9 importer fields corrected and all original GUIDs preserved**; then `GT_ORIGINAL_CLASS187_ARRAY_MATERIAL_LINKS` for **28/28 links** and all 9 source-target grids. 0 changes outside 9 image meta expected. Failures must be read by reason, no source image replacement by guessing.
2. Read `GT_REAL_ORIGINAL_BC3_EXACT_PNG_SLICES` and `GT_REAL_ORIGINAL_ARRAY_SOURCE_DECODER_LAYOUT`: color and layer ordering must be original before any Android pixel claim.
3. Build/verify Unity Editor import on disposable exported project using Unity 2021.3.45f2, inspect actual Texture2DArray class/mipmap/depth and Material slots; then hand off exact bounded patch to T5 native build. No original StreamData for ninth procedural or empty array; determine runtime initialization before inventing colors.
4. Further restore source shaders: proven 16 of 786 Dummy Materials repaired via TMP/PostFX/Volumetric, **770 remain**; unrelated original DXBC→Adreno variants not yet restored. Coordinate T3 and T5; don't claim all resources or device rendered.

## Durable links

- [GT MEMORY](../MEMORY.md), [STATE](../state.json), [RESTORE](../RESTORE_AR.md), [SUMMARY](../SUMMARY_AR.md), [GT↔T5 handoff](../discussions/20261112-T5-native-ZIP2-handoff.md)
- [source/BC3/shader evidence](../evidence/20261112_source_materials_original_bc3_arrays.json)

No game byte payload/GUID leaked in workflow artifact or Git files, no LFS and no zip2/main write.

## Real result: source importer restoration passed (not merely controls)

- **[43144656957 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43144656957)** actual full 134-ZIP2-source AssetRipper; `GT_REAL_SAFE_TEXTURE2DARRAY_GRID_REPAIR` confirmed `original_importer_repair_candidates_applied=9`, `postrepair_exact_original_layer_grids_validated=9`, `all_nine_original_array_importers_accepted=true`, `original_exported_asset_guids_preserved=true`, `source_images_or_binaries_edited=false`, `meta_files_outside_the_exactly_verified_array_set_changed=0`; byte-identical private backups. All 9 PNG images were complete source-aligned 1024px layer atlases. This is a *real isolated Unity export metadata correction*.
- Same run `GT_REAL_ORIGINAL_BC3_EXACT_PNG_SLICES`: source BC3 original byte recovery 69,906,400 verified; eight arrays with compressed pixels yielded **24 of 24 PNG/top-mip sample pixels byte-exact**, 8 of 8 independent source array layouts unambiguously `slice_major`; wrong `mip_major` candidate matched only 8 samples. Ninth original two-layer array still source zero pixel bytes and its runtime colors are NOT proven. No 11-mip parity or Android GPU.
- [Safe artifact 13911856847](https://github.com/alwansan/raf/actions/runs/43144656957/artifacts/13911856847) includes aggregate reports, not game imagery.
- [43145816256](https://github.com/alwansan/raf/actions/runs/43145816256): additional real test for original 28 Material ClassID187 links plus independent UnityPy decoded source images. Was still executing when evidence was first committed. Must inspect per-step before next completion claim.
- [T5 handoff updated](../discussions/20261112-T5-native-ZIP2-handoff.md), `state.json`, `MEMORY.md`, `SUMMARY_AR.md`, `RESTORE_AR.md` all carry verified proof. Branch only feature; no native XAPK in GT.
