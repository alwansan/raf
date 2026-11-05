# T3 — Exact original Particle108 third Texture2D absent B02 because collection nonexportable

**Verdict: SOURCE OBJECT CONFIRMED IN A NON-EXPORTABLE ASSETRIPPER COLLECTION. RENDER-002 OPEN / NOT_READY; NOT an Android pixel proof.**

## Real repeat export with minimal private classification

- [GitHub Actions 42132262184](https://github.com/alwansan/raf/actions/runs/42132262184) **COMPLETED SUCCESS** on source commit `aeca9d9c39132a448cf15ca3b357369deb6a7a4f`; **100/100 synthetic/source-free tests PASS** (12 Particle same-export +4 disposable instrumentation +13 original pass +7 Materials +23 Renderer +7 typed Texture +9 real stream contract +11 original range-guard +14 B05 same-export).
- Authenticated original ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, six original scenes, four Material/Shader owners, two runtime globals. One original image `.resS` provider full size+SHA verified and three source Texture2D ranges read. SHA-pinned public AssetRipperCLI commit `036098ab525a3f9f693dc101edeb21faad4d32d8` compiled; one actual export produced W1/B02 private traces sharing a single `export_instance`.
- Source→export baseline repeated **5/5 selected Material21 source identities** in exported trace and actual YAML, **2/3 Texture2D28 source identities** in B02 exportable trace, **9/10 exact Material texture PPtr matches**, **10/10 UV**, 0 source→null, 0 wrong GUID, 0 lost or extra TexEnv slots, 0 GUID collisions.
- New private-only instrumenter gathered original class28 objects from `collection.Exportable==false` collections, retaining their source owner/pathID ONLY inside ephemeral B02 JSON (never artifact). The ONE missing original Texture2D source identity was proven in that collection, not absent from all AssetRipper export collections: `selected_missing_texture_skipped_nonexportable_collection=1`, `selected_missing_texture_absent_all_export_collections=0`, `selected_missing_texture_reason_unclassified=0`.

## Causal interpretation

Original source Texture2D **EXISTS** and its `.resS` bytes were SHA verified. The B02 helper intentionally skips `collection.Exportable=false` Texture2D objects; hence its 2/3 population was a **trace coverage boundary**, not automatically lost original image data or broken exported Material. Actual Material YAML keeps the tenth source TexEnv slot and a nonnull pointer. Whether this pointer is a correct engine-builtin/nonexportable export reference, or is mismatched, has **NOT** been proven: need to privately evaluate `container.CreateExportPointer` for the skipped source object and compare it against the actual exported Material PPtr.

## Code and integrity

- `scripts/t3_stage_particle_nonexportable_trace.py`: asserts original W1+B02+B21 pinned helper composition and changes ONLY the copy staged in runner temporary files. Adds a PRIVATE list of nonexportable original class28 identities; does not change exported game asset selection or the shared production exporter.
- `scripts/t3_particle_same_export_bindings.py`: source-exact missing trace classified into `SKIPPED_NONEXPORTABLE`, `ABSENT_ALL_COLLECTIONS`, or `UNCLASSIFIED`. Counts only, no owner, source/asset PathID, Texture GUID, game bytes, property labels or private source paths in public output.
- `tests/test_t3_stage_particle_nonexportable_trace.py` four synthetic ownership/patching tests, and three added tests in `test_t3_particle_same_export_bindings.py` validate private missing-target classification and block false inferences. Initial [CI42132171708](https://github.com/alwansan/raf/actions/runs/42132171708) failed a synthetic fixture expecting 9 surviving bindings after removing a synthetic source Texture shared by TWO slots; fixture corrected to 8, then genuine CI42132262184 succeeded. This first failure is not evidence of a real source issue.

**No game shader/.meta/material, original texture asset, Unity native build, APK/OBB, audio, Settings, input, saved world, water or FFT changed.** Full-native/exporter parity and phone fire/smoke pixels remain unverified; `RENDER-002` remains OPEN.
