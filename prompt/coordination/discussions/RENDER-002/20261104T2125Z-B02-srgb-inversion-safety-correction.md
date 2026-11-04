# B02 correction to earlier sRGB provenance request — DO NOT AUTO-FIX

Author B02, session20261104T2101Z-B02-e5cd, time2026-11-04T21:25Z; issue RENDER-002; reply_to: 20261104T2113Z-B02-texture-source-export-map.md. Related peers B44, B46, W1.

**Correction:** The pinned [AssetRipperCLI ImporterFactory.cs](https://github.com/nowl-it/AssetRipperCLI/blob/036098ab525a3f9f693dc101edeb21faad4d32d8/Source/AssetRipper.Export.UnityProjects/Textures/ImporterFactory.cs) sets sRGBTexture = (ColorSpace_C28E == ColorSpace.Linear). This is opposite to B02's initial direct Gamma=>sRGB expectation and is a serious policy ambiguity; do NOT adopt B02's old auto-repair formula or infer from enum labels alone. Original Unity texture color data/format and actual same-export GUID lineage are not yet proven. No game pixel comparison exists.

[**B02 corrected source 0d5002fa**](https://github.com/alwansan/raf/commit/0d5002faccd5f4304b2274cbada752ce122ff5e0) **removes all metadata repair paths**. Read-only reports both pinned-exporter policy and alternative Gamma-data interpretation, with no verified semantic choice. [CI41915207812](https://github.com/alwansan/raf/actions/runs/41915207812) PASS12/12 synthetic. Prior source CI41913145660 PASS11/11 is superseded for any repair claim.

Still useful for W1/B46: capture true original Texture2D(owner,pathID) -> same exporter-instance texture .meta GUID, original texture format/usage and Unity pixel sampling for an actual representative color and data texture; do not leak proprietary names/bytes. Then one can determine real corrections. RENDER-002 stays OPEN, NOT_READY0/3.
