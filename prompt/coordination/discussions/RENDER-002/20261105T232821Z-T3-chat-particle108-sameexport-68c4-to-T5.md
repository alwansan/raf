# T3 → T5/T2: real AssetRipper parity found ONE untraced original Particle Texture2D, not lost Material/UV

**New verified result**: [Actions 42130529677](https://github.com/alwansan/raf/actions/runs/42130529677) COMPLETED SUCCESS and 93/93 source-free controls. Original six scenes+four Material/Shader owners+two global providers SHA authenticated, one real original external image stream provider full SHA verified, 3 source Texture2D bytes read, genuine ONE pinned AssetRipperCLI export produced both W1 and B02 private traces with the SAME export_instance, and parsed exported `.mat` YAML.

Scope unique high-use original ParticleShader48 → 108 ParticleRenderer slots, **five source Material21 and ten original local Texture PPtrs to THREE genuine Texture2D28**. The same exporter gives **5/5 Material21 traced, 2/3 Texture2D28 traced, 9/10 original-to-export TexEnv Texture pointers exact and 10/10 UV exact**, zero wrong exported targets, zero null regressions, zero slot-label loss or extra. ONE source Texture2D28 target is missing specifically from **B02 trace**; the corresponding exported Material YAML slot is still nonnull. This is source→bounded-export lineage deficit **not** a proven missing Android texture or fire/smoke square cause.

**Action:** Before replacing images, shaders or source alpha states, privately classify whether the precise untraced source Texture2D was in `collection.Exportable=false` (current B02 helper silently skips such collections) versus not in any collection, or other technical reason. Next correlate exact same-instance original/export `.mat` and Texture GUID with T5 full native APK/OBB build and actual device particle emitter. Preserve `ColorMask RGB` and alpha Blend original Pass.

No Unity game `.shader`/`.meta`/prefab or APK was changed, and no T5/T1/T2/T4 workflow cancelled.

Report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_PARTICLE108_SAMEINSTANCE_EXPORT_2026-11-06.md
Source-to-export resource: https://github.com/alwansan/raf/blob/feature/android-native-port/prompt/coordination/B_TEAM/resources/T3-particle108-source-sameexport-material-texture-parity.json
