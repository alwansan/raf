# W1 original Shader objects and Material links — 4 November 2026

[CPU41748891281](https://github.com/alwansan/raf/actions/runs/41748891281), job126308732596, source52e32cebb94011314e1b5761874bcb1102cc8cd4: **SUCCESS**. Local **60/60 W1 tests PASS**, including8original-linkage tests. No Unity or native delivery run was requested in this cycle.

## Proven original-source graph

All16authenticated providers,494208792bytes, were reused from pinned ZIP2/cache with no LFS or missing payload downloads. They contain165game Shader objects plus60canonical engine Shader objects. Across the selected game providers, all1544original Material Shader PPtrs resolve:763to verified engine keys,781to custom Shader objects,0unresolved. The16previously unresolved references all target the two original canonical engine resource files; each now requires both a real class48source object and its exact embedded engine database name/property key and engine-kind/pathID pointer match.

The canonical files are the already independently pinned Resources/unity default resources (4832808bytes,026e6d1d96dc2e28c72ece25f2419469d649a95e25b6929bc5cfc95bca529f8e) and Resources/unity_builtin_extra (936628bytes,0eb8f0a4ea47b075a6b637abc02d0c7930d96cb9f6c5d723819eb8042cfb3886). Game shader object count remains165; canonical nodes are counted separately.

## Duplicate identity is not a duplicate program

One original name+ordered-property key is shared by TWO game Shader objects. Their serialized payloads, parsed forms and decompressed platform-program sets all have distinct fingerprints. Each object is referenced by one original Material. Neither was merged, rewritten or omitted. This disproves treating the repeated key as a byte-identical copy; it does not establish their visual behavior. Exact member fingerprints are in the adjacent JSON report. Object IDs, original names and program bodies remain private.

Initial14provider runs [41748009438](https://github.com/alwansan/raf/actions/runs/41748009438) and [41748422989](https://github.com/alwansan/raf/actions/runs/41748422989) both succeeded and retained all16unresolved canonical references explicitly; the final16provider run resolves that source-coverage gap.

## Source closure is not export lineage

| Boundary | Material documents/objects | Engine shader references | Exported/custom shader references | Unresolved source Shader references |
| --- | ---: | ---: | ---: | ---: |
| Original selected16providers |1544|763|781|0|
| Actual native41741108965 post-restoration export |1536|750|786|No null/unresolved Material PPtrs reported;2newshader metadata errors|

These are different boundaries, not a per-object correspondence. Do not call the8count difference lost assets or assume which5references moved category. AssetRipper processing/redirect/export lineage must explain it.

Pinned public tool source [AssetExportCollection.cs](https://github.com/nowl-it/AssetRipperCLI/blob/036098ab525a3f9f693dc101edeb21faad4d32d8/Source/AssetRipper.Export.UnityProjects/AssetExportCollection.cs) constructs each collection GUID with UnityGuid.NewGuid(). Its source contains no owner/pathID-derived GUID formula. [ExportIdHandler.cs](https://github.com/nowl-it/AssetRipperCLI/blob/036098ab525a3f9f693dc101edeb21faad4d32d8/Source/AssetRipper.Export.UnityProjects/ExportIdHandler.cs) makes a normal Shader export fileID4800000. Therefore an original owner/pathID-to-exportGUID sidecar must be captured from the SAME actual export instance; guessing a GUID or borrowing one from another run is invalid. Preserve both same-key Shader objects and their Material edges in that capture.

## Remaining work

Trace original Material and Shader identity through the pinned processor/exporter collections and actual GUIDs, including legitimate predefined Material redirects and any shader reassignment. Validate the initial complete export before vendor fallback additions. Only then correct the builtin restorer's zero-loose-file assumption with source-linked actual export evidence. The current name-only full-export verifier deliberately rejects the repeated custom key.

Pinned engine196-record proof [41745967644](https://github.com/alwansan/raf/actions/runs/41745967644) is now confirmed **SUCCESS**; previous IN_PROGRESS checkpoints are superseded. Its750observed export engine references map to original engine keys; this is still not proof of per-Material preservation.

Native41741108965 remains **FAILED before Unity** at builtin0/142matches; no new APK/OBB/XAPK. Production builtin/water gates unchanged, original Material assignments in actual export unverified, water/FFT/rendering readiness OPEN, NOT_READY/0-of-3. No schedulers or protected branches changed.
