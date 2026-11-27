# G1/G2 — public exporter component capture witness

Pinned public source nowl-it/AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8. SceneExportCollection.GetExportID uses original serialized PathID or generated ID; CreateExportPointer(..., false) returns scene GUID/type2, local MetaPtr has zero GUID/type2 and writes fileID only. ExportableAssets excludes HiddenAssets. This patch scopes the optional component capture to exportable enumerations. New actual authored public-tool C# witness, build pending; no original acquisition or export.
