# GT — دورة Chat-08: استعادة صفائف المصادر داخل مسار Unity Android

- session_id: GT-20261112-CHAT-08-NATIVE-ARRAY-IMPORT-GATE
- origin: chat; agent GT; writable branch feature/android-native-port only
- Original: zip2 @15964ea8f246b6e076ce26b60931ee2e1a9a2385, manifest SHA256; absolutely no Git LFS
- No writes to main or zip2; do not trigger or cancel T1–T5 native APK/XAPK jobs

## Source verified

- [Real 43144656957 PASS](https://github.com/alwansan/raf/actions/runs/43144656957): exact 134 original ZIP2 resources→same-instance AssetRipper, nine PNG source-complete ClassID187 Texture2DArray atlases. Nine zero/missing flipbookRows/Columns repaired with exact original GUID, 0 PNG alterations, 0 unrelated .meta changes, private backups. Recovered source BC3 69,906,400 bytes for 50 populated original layers; ninth two-layer array has zero original stored pixel bytes and is not invented. 24/24 sampled original DXT5 top-mip pixels match actual exported PNG; eight arrays unambiguously slice-major.
- [Real 43145816256 PASS](https://github.com/alwansan/raf/actions/runs/43145816256): 28/28 source original Material TexEnv class187/fileID18700000 pointers intact to all nine same-instance original PNG GUIDs and verified importer grids. Safe [artifact](https://github.com/alwansan/raf/actions/runs/43145816256/artifacts/13912786902). No actual Unity Editor import or device GPU claim.
- Source graph still 10,216 original TexEnv properties and 4,151 internal links exact; 416 external target identities not fully proven. Vendor shader correction 786 raw Dummy Material docs→770; 770 remaining.

## Integrated production native pipeline

- In .github/workflows/raft-unity-editor-android-import.yml: after original SHA-pinned ZIP2→AssetRipper export and before Material/B04 gates, GT validates 9 original ClassID187 importer PNG atlases; corrects only flipbookRows/Columns from authenticated source, preserving every original GUID and PNG byte; strict 28 real Material PPtr verification. Original native build and T5/Water/Shader delivery gates remain intact and not triggered.
- B46 script verify_exported_material_texture_links.py recognizes real imported array fileID18700000 only with original Unity shape4, positive grid and valid PNG IHDR dimensions. It rejects falsified shape4 image with Texture2D fileID2800000 and retains ordinary fail-closed Texture2D guards.
- scripts/gt_write_unity_array_import_contract.py writes private Assets/Editor/RaftAndroid/GTOriginalArrayImportContract.json containing exact nine source-authenticated GUIDs, 52 logical layers, 50 source pixel-bearing, depth/width/height/mipcount. This private manifest is not uploaded to GitHub Actions artifacts.
- android-port/Editor/OriginalTextureArrayImportGuard.cs is invoked by AndroidNativeBuild.ValidateSdkBindings and Build. It tests actual Unity Editor native Texture2DArray loaded class, original GUID, depth/size, 11 expected mips, flipbook grid, 9 arrays/52 logical layers/50 from original stored pixels. Fails build if Unity imports wrong type or shape; this is NOT a claim Unity Editor has run.
- Synthetic Python/native structure and source-free .NET CSharp compilation [43150348740 PASS](https://github.com/alwansan/raf/actions/runs/43150348740). CSharp harness uses stubs, so only syntax and API-shape checked. Existing native workflow change does not run APK by itself.

## Pending, no overstatement

- Isolated real full AssetRipper action [43150158897](https://github.com/alwansan/raf/actions/runs/43150158897) tests the nine-GUID temporary Editor manifest after real 28 ref checks. At first checkpoint its completion was not confirmed; read step-level GT_NATIVE_PRIVATE_UNITY_ARRAY_GATE output.
- Unity Editor 2021.3.45f2 actual import of native Texture2DArray, Android Adreno pixels, full 11 mip-chain, gameplay/FFT/water, and new signed XAPK are NOT verified.
- Coordinate with T5 before authorized native build; do not bypass prior strict water/shader/authenticity gates or create source-image placeholders.

Files: clients/GT/MEMORY.md, state.json, SUMMARY_AR.md, RESTORE_AR.md and discussions/20261112-T5-native-ZIP2-handoff.md; evidence in clients/GT/evidence/20261112_source_materials_original_bc3_arrays.json.
