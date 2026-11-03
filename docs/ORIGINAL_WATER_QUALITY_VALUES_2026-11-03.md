# Original water quality resource values — 3 November 2026

This investigation changes analysis/test code only. It does not change original quality values, assets, shaders, game settings, native requests or scheduled automations. Unity/APK/OBB/XAPK/release hold remains active.

## Provenance

- Source f9f9f46d4b62d56bc39a64d16309a444b7fb719a; [original resource inspection41554294910](https://github.com/alwansan/raf/actions/runs/41554294910), job125649268355, SUCCESS. Exactly one111,533,516-byte LFS owner was hydrated: resources.assets SHA25687493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c. No resS stream or full checkout was fetched.
- The same resources.assets was independently restored locally from the owner's verified six-part archive and matched that exact size/SHA. Reuse these authenticated local bytes for future inspections; an additional original-data download was not needed for decoding.
- One exact typed MonoScript-linked quality component was found: resources.assets pathID6376,476bytes, SHA256c8ee04ce0ad9965caa4a2862d4d305501ddae5a1c596ce78bb89be390970b15b. Its actual script PPtr resolves to globalgamemanagers.assets/pathID838, script SHA2562bb072a5ddf603e75cba9da4b7e6429c140ca95a9631495802b952e4c2f629c6. The global script owner SHA is b549af329d48244d80f28cb3cce6cd0b17769176081c249dc4646e1d62c58e28.
- Only encrypted selected original object/source bytes left the runner. The session decrypted the packet privately, verified its source commit and all file hashes. [Nested source-only inspection41554501052](https://github.com/alwansan/raf/actions/runs/41554501052), sourcec8b68b618d3c9f635dc0290e4311b9cc4c4e4078, SUCCESS; all131 manifest file hashes were verified. This follow-up fetched no LFS.

## Schema boundary

The original source has inline ripple data before the quality array. It is six serialized fields, not an object pointer. Initial exploratory offset interpretations were rejected and did not modify resources or produce accepted results. The accepted decoder uses the source-correlated field sequence, four-byte boolean alignment and bounded strings, verifies the exact original object hash and consumes all476bytes without trailing data.

Four original CSharp9 source hashes are pinned in scripts/probe_original_water_quality_values.py: WaterQualitySettings, WaterQualityLevel, WaterRipplesData and WaterWavesMode. All four were verified for the local original-data decode. Tests reject fingerprint drift, truncation, trailing bytes, invalid booleans/alignment/enums/indices and nonfinite floats. No original names or raw bytes appear in public fixtures or diagnostic JSON.

**This is a source-corroborated serialization-layout decode, not an authenticated complete Unity TypeTree recovery or a phone measurement.** Original full_typetree_verified remains false. Preserve this distinction when using the following values.

## Decoded stored quality limits

| Serialized index | Spectrum resolution maximum | High precision | High-quality normal maps |
|---:|---:|---|---|
|0|32|false|false|
|1|64|false|false|
|2|256|false|false|
|3|512|false|true|
|4|512|false|true|
|5|256|true|true|
|6|256|true|false|

All seven stored limits are powers of two. The saved custom index is6; synchronization with Unity is true. **Index6 must not be treated as the active device setting.** Original source first tries to resolve Unity's current quality name and otherwise uses/clamps the saved custom index. Scene/requested water resolution and device maxTextureSize still affect the final minimum proven by the earlier owner-property probe.

The inline ripple iteration field decodes as0 and its shader mode as1; these are preserved original stored values. They are not evidence that enabling/changing them would repair missing water. No quality increase/decrease, shader substitution or fake kernel was introduced.

## Validation and remaining work

Source2546f795853ec1923e3bccd1ca76f8305160a0c6 adds the pinned decoder and corruption fixtures. Local22 related tests passed; the exact original object and four schema-source hashes passed local decoding. [Synthetic/no-LFS preflight41554799751](https://github.com/alwansan/raf/actions/runs/41554799751): **SUCCESS**, job125650951130, including all four new corruption/schema fixtures. This preflight does not read the original private object and must not be called an original-data CI decode.

Next authenticate actual serialized per-water requested resolution and its scene linkage, and determine the active quality selection and device texture limit. Then validate format compatibility, numerical FFT semantics and Unity kernel-index interpretation. The strict water authenticity gate remains blocked. Source defaults and stored maxima alone cannot establish the active constructor size or correct rendered water.

Last game release remains APK80/source9462f8edd8cdb5becbccb96521f2876ef9924410 with11 delivery assets; checked independently from newer lograf releases. None of this analysis is an installed-device trial.
