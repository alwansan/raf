# T3 — Real AssetRipper particle nonexportable Texture2D pointer parity: tenth binding verified

**Verdict:** Original high-use Particle Shader48's selected five Material21 source objects now have **10/10 exact source→same AssetRipper export Texture PPtr matches** (9 ordinary exported Texture2D pointer matches + 1 direct pointer for a nonexportable source Texture2D), and **10/10 UV transforms**. This is **one bounded authentic source/export invocation**, NOT Unity Android/Adreno rendering acceptance. `RENDER-002` stays **OPEN / NOT_READY**.

## SHA-authenticated inputs and terminal execution

- [Actions run 42134436841](https://github.com/alwansan/raf/actions/runs/42134436841) **COMPLETED SUCCESS** on exact workflow source commit `eeecaae71e20df2abac7e7bb5693aa7e20c5e7e5`. Python synthetic and strict controls **16+4+13+7+23+7+9+11+14 = 104/104 PASS**; public AssetRipperCLI source pinned at `036098ab525a3f9f693dc101edeb21faad4d32d8` compiled and ran on the original inputs, and actual exported Material YAML was parsed.
- The private original source graph was reselected from six SHA-pinned scenes and four SHA-authenticated original Shader/Material owners, with two additional authenticated runtime global serialized providers, from the immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. One original `.resS` provider was reconstructed/verified end-to-end by manifest size plus SHA; exactly three source image ranges were re-read from it.
- Exactly **108** original ParticleRenderer material-slot references use the selected original Shader48, comprising **5** distinct genuine source Material21 objects and **10** non-null `m_TexEnvs` local Texture2D pointers to **3** actual source class28 Texture2D objects. The source original Pass render state is ColorMask RGB with alpha-dependent blending; no executable shader source was edited.
- W1, B02 and B21 optional private traces all used **the SAME AssetRipper export instance**, not combined from different exports. Actual `.mat` YAML was parsed with duplicate mapping key defenses and compared against the source-identified Material TexEnv properties and UVs.

## Actual same-export result

| Scoped authenticated original-source→real-export measure | Count |
|---|---:|
| Original selected Material21 objects in W1 same-export trace | **5 / 5** |
| Original Texture2D28 objects in B02 exportable collection trace | **2 / 3** |
| Third original Texture2D28 identified in `collection.Exportable=false` | **1 / 1** |
| Source Material Texture pointers matching expected ordinary exported Texture2D pointer | **9 / 9** |
| Third source nonexportable Texture2D's `container.CreateExportPointer(asset)` resolved from SAME instance | **1 / 1** |
| Source Material Texture pointer matching that actual nonexportable container pointer | **1 / 1** |
| **Total source→export Material Texture pointer matches** | **10 / 10** |
| Source Material original UV scale/offset values equal exported YAML values | **10 / 10** |
| Source target unresolved due missing B02 record after private pointer comparison | **0** |
| Selected Material TexEnv null regression or wrong GUID | **0** |
| Missing or extra selected exported Material TexEnv property | **0** |
| Nonexportable source pointer unreadable, missing or mismatch | **0** |

The prior **9/10** report was a limit of the B02 trace, NOT an actual tenth exported Material GUID mismatch. The third source Texture2D was intentionally excluded from the list of `collection.Exportable=true` objects. A disposable private instrumenter called `container.CreateExportPointer` on precisely this source object within the same original AssetRipper instance. The resulting **non-null pointer exactly matched** the tenth actual exported Material YAML `m_TexEnvs` pointer. No source, private GUID or pathID was guessed or publicly serialized.

**Precise boundary:** This does not mean three Texture2D objects became three separate exported Unity Texture assets: only two were in exportable collections; one was correctly addressed via its nonexportable/internal pointer. It establishes pointer identity parity for the source-selected five Materials in this one bounded exporter. It does **not** prove that the actual complete native Android Unity build has corresponding Material GUIDs, image decoding and sRGB/alpha/sampling, or that the selected Particle Shader48 belongs to the user's visibly square fire/smoke emitter. Real Android fragments/pixels remain unverified.

## Implementation and privacy controls

- `scripts/t3_stage_particle_nonexportable_trace.py`: only the SHA-checked **disposable** W1+B02+B21 C# helper is modified. A private `container_export` pointer plus boolean capture status is written for nonexportable class28 objects; runtime pointer capture failures are reported as null/capture=false with no exception text. **No export selection, game asset or production helper altered**.
- `scripts/t3_particle_same_export_bindings.py`: the three-way private source ID→same-instance export pointer→actual Material YAML comparison distinguishes exact ordinary exportable pointer matches, exact nonexportable container pointer matches, unavailable pointer and wrong pointer; all reports are anonymous aggregate allowlists. A scoped `SAME_INSTANCE_SOURCE_PARTICLE108_NONEXPORTABLE_CONTAINER_POINTER_PARITY` verdict is not an Android READY flag.
- Synthetic tests in `tests/test_t3_particle_same_export_bindings.py` include exact tenth pointer success, wrong nonexportable pointer, inaccessible pointer, malformed/duplicated source report, cross-instance contamination, UV drift, missing Material and wrong GUID. `tests/test_t3_stage_particle_nonexportable_trace.py` asserts the exact C# container pointer helper/catch branches and protects the shared W1 source from modification.
- The dedicated `.github/workflows/raft-t3-particle108-sameexport.yml` compiled a public pinned exporter and staged exact source bytes only inside the transient GitHub runner; uploaded ONLY safe numeric aggregate artifacts, never `m_PathID`, Material/TexEnv property names, Texture GUIDs, original game bytes or private W1/B02 JSON.

## Engineering implications / next handoff

Do **not** attempt to 'restore the missing third Texture2D' or replace it with an opaque/dummy texture based on B02's previous 2/3 count: it is not a proven missing image. Preserve source ColorMask RGB/alpha blend and Material textures. **Next meaningful test** is to identify the exact game ParticleSystemRenderer responsible for square fire/smoke on the installed Android build and verify the generated/shipped fragment shader (texture sampling and alpha/discard), the real TextureImporter/color formats/decoded pixels, and native Unity/OBB resources. Coordinate T5's next APK/OBB and device logs/screenshots; do not cancel another worker's build.

**Game resources unchanged:** no `.shader`, `.meta`, scene, prefab, texture, OBB, APK, audio, Settings, input, water/FFT or world/save file modifications were made. `RENDER-002` remains OPEN / NOT_READY until real Android pixels pass.
