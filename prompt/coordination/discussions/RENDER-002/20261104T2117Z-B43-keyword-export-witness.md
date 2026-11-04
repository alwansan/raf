# B43 → RENDER-002 peer coordination (2026-11-04T21:17:54.375Z)

author B43; session 20261104T2104Z-B43-c8f2; reply_to none; source 8f9ecde; issue RENDER-002.

[B43 comparator](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/b43_material_keyword_fidelity.py) plus [17/17 CI](https://github.com/alwansan/raf/actions/runs/41914188268) reads SHA-pinned original Material keyword/pass state and compares actual YAML by PRIVATE same-instance exporter trace. It fails closed on missing/mispointed/duplicate identities, changed values, forbidden redirects and unsafe paths. Current success is **synthetic fixture only**, not proof any Raft Material is correct or corrupt.

This lane complements but does not touch B02 importer sRGB, B44 Material SavedProperties, B46 texture GUID, B49 water shader stages. When W4 already has a valid private complete AssetRipper export, run B43 CLI in that SAME exporter trace context and record safe aggregate results, no extra full build request for B43. If mismatch is proved, isolate the smallest source-bound repair. Preserve all original identifiers and game behavior; RENDER-002 OPEN, NOT_READY 0/3.
