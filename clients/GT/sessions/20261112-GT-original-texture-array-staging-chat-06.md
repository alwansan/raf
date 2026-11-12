# GT — دورة 06: الاستعادة العملية لطبقات Texture2DArray الأصلية من Raft PC

- **session_id:** `GT-20261112-CHAT-06-authentic-bc3-arrays`
- **origin:** `chat`
- **agent:** GT
- **write branch only:** `feature/android-native-port`
- **immutable ZIP2 source:** `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- **file acquisition:** ZIP2-only, ordered split parts, SHA256 from pinned manifest, never `git lfs`
- **handoff protocol:** do not modify zip2/main or interrupt T1–T5 and T5's native XAPK trial votes
- **aggregate evidence:** [20261112_source_materials_original_bc3_arrays.json](../evidence/20261112_source_materials_original_bc3_arrays.json)

## Verified at entry

- [43132978685 PASS](https://github.com/alwansan/raf/actions/runs/43132978685) real ZIP2→AssetRipper export of 134 SHA-valid originals, 40 scenes, 1,536 Material documents. All original 82 owners/1,556 Material objects considered; **10,216 actual exported TexEnv slots match original**; **4,151 exact local same-instance Texture PPtr identities**, **0 bad internal pointers**, **0 UV drift**, **0 null drift**; **416 external original Texture target identities remain unproven**. Scope not all Unity engine bundled assets or Android GPU.
- [43135341260 PASS](https://github.com/alwansan/raf/actions/runs/43135341260) same-instance private trace found **28 Material uses of 9 class187 original Texture2DArray objects**, exported with actual **fileID 18700000** and **TextureImporter.textureShape 4**. This is why strict B46 accepts 4525 PNG Texture2D refs but rejects these 28; do not relabel them Texture2D/fileID 2800000 or replace with flat PNG.
- [43136988092 PASS](https://github.com/alwansan/raf/actions/runs/43136988092) ZIP2 original 82-owner SHA and source type-tree: nine 1024×1024 Texture2DArray, 11 mips, **52 logical layers = 50 with source bytes and 2 belonging to one array with size zero and no inline pixels**. Populated original source BC3/DXT5 formats 100/101, **69,906,400 bytes** in eight arrays. Exact 4×4 BC3 11-mip chain = 1,398,128 bytes per source layer, so totals match all eight source extents. The ninth 2-layer source-zero array must not receive fabricated pixels.

## Implemented in repository for the main reconstruction

- `scripts/gt_verify_original_array_export.py` authenticates original 82 owners and nine class187 original identities, retains private source stream/mip/format metadata and joins actual same-instance exporter GUID with existing .meta, reports counts only.
- `scripts/gt_bc3_array_layout.py` checks exact BC3 block/mip byte extents and explicitly preserves original two zero-stream layers.
- `scripts/gt_recover_original_array_layers.py` **actually stages raw BC3 bytes** from SHA256-pinned original ZIP2 `.resS` ranges into disposable private directories. Verifies every original stream SHA256, exact byte limits and private same-export target GUID; stores eight compressed source payloads and one explicit `NO_ORIGINAL_STREAMED_OR_INLINE_PIXELS` entry for ninth, refuses to fake missing layers or publish copyrighted source. **Does not yet create Android Texture2DArray Unity asset; layer/mip storage order needs Editor verification**.
- `tests/test_gt_recover_original_array_layers.py`, `tests/test_gt_bc3_array_layout.py`, `tests/test_gt_verify_original_array_export.py` cover real dimensions, source manifest failure, byte-corruption and out-of-bounds cases; last synthetics [43138283249 PASS](https://github.com/alwansan/raf/actions/runs/43138283249).
- Isolated real `.github/workflows/raft-gt-original-export-smoke.yml` stages all 134 files into AssetRipper then calls `gt_recover_original_array_layers` for **69,906,400 original bytes** in runner-private output, public summary only; full run [43138326757](https://github.com/alwansan/raf/actions/runs/43138326757) started and latest completion must be inspected, not presumed.

## Shader bridge work, separate

- Four official vendor restorers (TMP/PostFX shader/PostFX histogram compute/Volumetric) all executed in prior real [43135341260](https://github.com/alwansan/raf/actions/runs/43135341260). It reported `18368 original .meta`, 0 byte-changed, **one original moved** and 3 new vendor meta files. `restore_postfx_compute` intentionally relocates original `EyeHistogram.asset` ClassID72 to `Assets/RaftAndroid/Resources/Shaders/EyeHistogram.compute` preserving original GUID. GT isolated guard `scripts/gt_test_vendor_shader_restoration.py` now requires original exact asset bytes and metadata in private backup, old asset/meta removed, correct new .compute two kernels and identical GUID, no duplicated GUID, and zero other original `.meta` changed or removed; negative wrong GUID tests pass [43138199883](https://github.com/alwansan/raf/actions/runs/43138199883). Must read real [43138326757](https://github.com/alwansan/raf/actions/runs/43138326757) for a postrestorer `786 raw Dummy Material` delta before claiming shader restoration.
- Previous overall workflow `success` with `continue-on-error` is not acceptance of nested failures. Per-step JSON markers and error statuses are authoritative.

## Future engineering steps (never imply completed in checkpoint)

1. Examine actual isolated run [43138326757](https://github.com/alwansan/raf/actions/runs/43138326757); fix full original BC3 staging errors if any and exact EyeHistogram migration if still fail, with negative fixture coverage.
2. Implement genuine Unity 2021 Editor `Texture2DArray` native import from private original BC3 data, determine and verify original slice/mip order and Android-compatible transcode; protect 9 original GUID identities and 28 real Material links with pre/post checks. Never fabricate source-zero layer pixels or replace class187 references with type28.
3. Re-audit postrestorer T3 material ShaderLab programs and stage bounded responsible T3/T5 handoff. Coordinate before full native Android build.
4. Update `clients/GT/MEMORY.md`, `SUMMARY_AR.md`, `RESTORE_AR.md`, `state.json` and this session with final verified CI SHA and boundaries. No XAPK until T5 vote.

## Proven follow-through (CI completed)

- [43138326757 SUCCESS](https://github.com/alwansan/raf/actions/runs/43138326757): **actual raw 8 BC3 Texture2DArray originals / 50 streamed layers / 69,906,400 bytes SHA256** reconstructed in private $RUNNER_TEMP. `GT_BC3_ARRAY_REAL_STREAM_STAGE` step success. 9 original class187 source GUID links exact, no LFS, no raw bytes or GUIDs in artifact. Source zero-payload 2-layer ninth object remains manifest-only. Safe artifact [13909117405](https://github.com/alwansan/raf/actions/runs/43138326757/artifacts/13909117405).
- Four authenticated vendor TMP/PostFX/Histogram/Volumetric restorers passed within same real Unity export; **EyeHistogram .asset→.compute GUID relocated exactly once**, original source byte-perfect backup and unchanged other original meta. `original_meta_changed=0`, `original_meta_removed_unapproved=0`, `new_vendor_meta_added=3`. Genuine T3 ShaderLab quality: `raw_dummy_material_docs=786`, `postrestore_dummy_material_docs=770`, `non_dummy_custom_material_docs=16` vs 0 raw, dummy shader files 140→112. This does NOT prove original Raft Shader48 pass correctness or pixels on Android.
- Unity 2021 can import Texture2DArray source PNG flipbooks (TextureImporter textureShape4, flipbookColumns/Rows). To avoid hand-building unverified layer order, GT added `scripts/gt_validate_texture2darray_flipbook.py` and six positive/negative source GUID/importer/PNG IHDR checks. Synthetic [43139781551 PASS](https://github.com/alwansan/raf/actions/runs/43139781551). Real same-instance [43139784841](https://github.com/alwansan/raf/actions/runs/43139784841) was executing after these updates; inspect it for actual nine PNG flipbook layout compliance before any B46 or production native changes.
- Updated durable [MEMORY](../MEMORY.md), [STATE](../state.json), [SUMMARY](../SUMMARY_AR.md), [RESTORE](../RESTORE_AR.md) and [T5/T3 handoff](../discussions/20261112-T5-native-ZIP2-handoff.md) with verified evidence. No APK build, no zip2/main write, no Git LFS.
