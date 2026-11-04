# B02 — TextureImporter sRGB fidelity guard for original Raft materials

**Track:** RENDER-002 (P0 colors/materials); **client:** B02; **session:** 20261104T2101Z-B02-e5cd.

## Why this work is separate

W2's authenticated original probes established original `Linear` player color space and original Texture2D `m_ColorSpace` Gamma/Linear distribution. Gamma texture data needs Unity sRGB sampling (`TextureImporter.sRGBTexture=1`), whereas original explicitly Linear data needs `0`; dropping the distinction can affect albedo/normal/mask display even with correct shader and Material links. B44 is addressing serialized Material values, B46 `m_TexEnvs` links, W1 source Shader identities; B02 does not modify their work.

## Implementation and security contract

`scripts/b02_texture_import_color_guard.py` checks only EXPLICIT same-export original `(owner,pathID)` -> exported `(asset path, GUID)` links. It neither predicts AssetRipper GUIDs nor assigns textures by filename. Sidecar is an input, **not independent proof of link provenance**; `same_export_linkage_independently_verified` remains **false** until a same-instance exporter witness is captured and verified. It requires one exact `TextureImporter`, one `sRGBTexture`, one GUID, no duplicate links, no symlinks, and safe relative paths. Missing/ambiguous metadata fails rather than guessing Unity defaults.

On `--original`, each source owner is size/SHA256 authenticated and its Texture2D `pathID` and `m_ColorSpace` are re-read through UnityPy. `--repair` cannot run without this source verification. Repairs adjust only the targeted numeric `sRGBTexture` flag in export-side `.meta`, preserving the GUID and other lines; this command is **not run on project assets** until a trustworthy same-export mapping exists. No original game bytecode, shader sources, textures or per-object IDs are printed; report contains counters and explicit false runtime stages.

## Test matrix / remaining gates

The isolated B02 workflow runs synthetic correct Gamma/Linear flags, wrong flag detection, absent/duplicate metadata, wrong GUID, duplicate identity, symlink/traversal attacks, repair refusal without original bytes, source hash/pathID/color mismatch, authenticated synthetic rewrite, and aggregate-only output controls. These are structural/algorithmic tests only. The source-owner test uses an artificial 8-byte owner and stubbed UnityPy; it is **not** a real Raft asset test. Before production adoption, obtain a SAME EXPORT instance identity sidecar and authenticate original asset bytes; then run a read-only mismatch inventory first, retain patched original GUIDs, re-import with Unity, compare controlled reference pixels, and test APK on the phone. RENDER-002 stays OPEN / NOT_READY / independent readiness reviews 0/3. Audio and Settings unchanged; deferred touch untouched; no full native build requested.
