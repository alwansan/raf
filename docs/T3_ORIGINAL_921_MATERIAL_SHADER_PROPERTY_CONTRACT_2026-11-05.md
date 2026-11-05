# T3 — authentic 921-use original Shader48 → Renderer-linked Material properties (2026-11-05)

**Issue:** RENDER-002 OPEN, NOT_READY 0/3. Real source CI [42080105181](https://github.com/alwansan/raf/actions/runs/42080105181) COMPLETED SUCCESS, **37/37** source-free tests (25 T3 new + 12 inherited original Renderer tests). Public-safe seven-day artifact t3-original-921-material-property-safe-42080105181, artifact id 13439229416 (1,010 bytes).

## Distinct engineering question

Previous same-export material parity for 41 original Materials in sharedassets6.assets proved 227 TexEnv/UV and 150 RGBA slots match, but those 41 assets are a different population than the Renderer-linked materials of the most-used original Shader48. Earlier true original source → same-instance export [CI42044249541](https://github.com/alwansan/raf/actions/runs/42044249541) verified that the top original 921-Renderer-slot Shader48 still maps to a default AssetRipper Dummy ShaderLab file after ONLY TMP/PostFX/Volumetric vendor replacements. That isolated export is NOT proof of what the current full native build actually imports.

Question here: do the original Renderer-linked Materials have original m_SavedProperties names in the correct types/families declared by their actual linked original Shader48 (m_ParsedForm.m_PropInfo.m_Props), or are some field names absent/mistyped at source?

## Source authenticity, population, contract

- Immutable original ZIP2 commit: 15964ea8f246b6e076ce26b60931ee2e1a9a2385. Six real PC scenes level0–level5 and four Shader/Material owner blobs SHA+size verified (269,007,288 owner bytes, without LFS).
- Reused T3's original Renderer→Material→Shader48 source identity and strict one-based external m_FileID resolution. Independently re-read source Renderers and traversed exact source class21 m_Shader pointer. Selected uniquely the one original Shader48 referenced by **921** original Renderer Material slots, across **43** distinct original Materials, among the verified total 1,639 Material slots/1,633 typed Shader48 references/21 typed Shader48 objects.
- Declared Shader property enum m_Type=0 Color, 1 Vector saved with colors, 2 Float and 3 Range saved as floats, 4 Texture saved with TexEnv. Source-specific type/name mapping stays private. Existing B05, B44, B22 original SavedProperties parsers reused without edits. No original shader bytes, proprietary property names/values, private IDs, GUIDs or per-object SHA printed.

## Genuine original source observations

| Selected original Shader48 + 43 Material objects | Count |
|---|---:|
| Original Renderer material-slot occurrences | **921** |
| Distinct original Material objects | **43** |
| Original Shader property declarations | **35** |
| Declared texture / color+vector / float+range types | **6 / 5 / 24** |
| Declared property-to-saved correct-family matches | **1,505/1,505** |
| Declared property names absent / without a correct saved family | **0 / 0** |
| Original Materials with all declarations saved correctly | **43/43** |
| Saved TexEnv entries / non-null texture pointers / null pointers | **258 / 144 / 114** |
| Materials with at least one declared non-null texture | **43/43** |
| Original saved Colors / float entries / int entries | **307 / 1,816 / 0** |
| Extra distinct saved names not declared by selected Shader (summed per Material) | **875** |
| Original Materials containing extra saved names | **43/43** |
| One original saved property name present across two distinct families | **1** |
| Original Renderer slots affected by that cross-family name | **3** |
| Wrong-family saved entry for an original declared property, *with correct family also present* | **1** |

**Supported conclusion:** All 43 source Material objects contain the high-use Shader48's 35 declared property names in the correct SavedProperties family. Source-original missing declaration/family is not a demonstrated explanation for these white materials. The 114 genuine source-null texture pointers, 875 extra saved names and single dual-family source name are not proof of a broken Android export; default textures, legacy saved names and actual shader program reads require separate runtime evidence.

**Not proven:** actual source→same-export identity/values for these 43 (distinct from previously verified 41); current full Android AssetRipper/ShaderLab imports, shader bindings, samplers/CB layout, keywords, colors/sRGB, GPU pixels, water, world gameplay or pixel fidelity. The high-use Shader remains a confirmed bounded-export Dummy risk from CI42044249541, but there is no new native game patch here.

## Implementation and resolved negative trials

- New script [t3_original_921_material_property_contract.py](../scripts/t3_original_921_material_property_contract.py), tests [test_t3_original_921_material_property_contract.py](../tests/test_t3_original_921_material_property_contract.py), isolated SHA-verified workflow [raft-t3-original-921-material-property.yml](../.github/workflows/raft-t3-original-921-material-property.yml); origin chat session 20261105T1745Z-T3-chat-921-shader-material-property-7a6e. The original source SHA-only job is CPU based, marker-only explicit, with no native Unity build or Actions cancellation.
- [CI42078619189](https://github.com/alwansan/raf/actions/runs/42078619189) original SHA authenticated but initial experimental parser inconclusive ValueError. [CI42079152807](https://github.com/alwansan/raf/actions/runs/42079152807) isolated PRIVATE_PROPERTY_FAMILY_JOIN. [CI42079640985](https://github.com/alwansan/raf/actions/runs/42079640985) isolated real source OVERLAPPING_PROPERTY_FAMILIES without disclosing names. Our new assumption that original Unity Material saved names could not recur across different property-family arrays was false. Corrected by preserving each name's **set of serialized saved families**, counting dual-family names separately while keeping wrong-family entries visible rather than dropping one. [CI42080105181](https://github.com/alwansan/raf/actions/runs/42080105181) original SHA authenticated and fully classified **SUCCESS**, 25 new + 12 inherited tests passed.
- Safe aggregate artifact t3-original-921-material-property-safe-42080105181; source original bytes and all Material names and values stayed in disposable runner. No game assets, .meta, Unity shaders or workflow owned by T1/T2/T4/T5 changed.

## Concrete handoff

Do **not** rewrite the 43 Material SavedProperties; source names and correct families are intact. Focus next on real ShaderLab pass/program and binding fidelity of the high-use source Shader48 in the **full current native restorer/export stage**, rather than default Dummy or guessed HLSL. Compare exact source original four Passes / 33 matched variants / texture sampler/CB requirements to current compiled project and then test on Android Adreno. CI42076083800 already proved 4/4 source and roundtrip numeric SPIR-V stage interface, not shader value or device equivalence. Keep RENDER-002 OPEN, protect working audio and Settings, leave touch deferred.
