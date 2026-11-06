# T3 — all four exact original Particle108 DXBC Vertex/Fragment semantic and component-mask joins match

**Verified:** Four authenticated original PC Raft ParticleShader48 D3D11 Vertex/Fragment keyword pairs have **4/4 complete authored VS→FS user semantic/type/component-mask compatibility**. Across pairs, 16 user semantic records, 58 component lanes, ZERO missing fragment inputs/lanes, ZERO missing Vertex output component lanes, ZERO matched semantic component-type mismatch. This is the compiled *source* baseline, not proof of reconstructed HLSL/Android shaders. `RENDER-002` **OPEN / NOT_READY**.

## Real pinned inputs and tool execution

- [GitHub Actions 42146385054](https://github.com/alwansan/raf/actions/runs/42146385054) **COMPLETED SUCCESS** on exact workflow source SHA `1ed58e7beab792c877edeaeab163a78c5ba23303`, **147/147** synthetic and inherited Python tests PASS (23+13+9+12+5+7+6+7+7+9+11+5+11+22).
- Original PC Raft immutable ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`: exact six original scenes and four original Shader/Material owners size/SHA authenticated, plus independently restored original `.resS` provider full SHA and three source Texture2D span reads. No LFS source substitution or game byte upload.
- Original selected *unique* one-normal-Pass Shader48 defined by **108 ParticleSystemRenderer Material uses on 54 distinct Renderers**, five true Material21 and ten source Textures (10/10 original same-export Texture PPtrs from previous genuine AssetRipper CI42134436841). Four authentic DXBC stage keyword permutation pairs and eight true source-stage program containers validated with original platform4 table indices.
- Existing **strict actual DXBC signature reader**, `scripts/t3_original_921_dxbc_semantic_join.py` from earlier separate original top921 work, reused unchanged to parse original source `ISGN`/`ISG1`, `OSGN`/`OSG5`/`OSG1` and compare private authored semantic string+index, type, component output/input masks. Existing `t3_dxbc_signature_contract.summarize_signature` refuses duplicate register component ownership, unsupported source chunks and malformed DXBC. No inferred SPIR-V Location was used.

## Real original DXBC authored semantic outcome

| Original genuine DXBC measure (four pairs) | Result |
|---|---:|
| Exact original Vertex+Fragment keyword pairs | **4** |
| DXBC source stage programs read | **8** |
| Original input signature records across stages | 34 |
| Original output signature records across stages | 24 |
| Input signature system-value records | 6 |
| Output signature system-value records | 4 |
| DXBC ISGN signature chunks | 8 |
| DXBC OSGN signature chunks | 8 |
| Original user Vertex output semantic records | **16** |
| Original user Fragment input semantic records | **16** |
| Original VS→FS authored semantic+index pairs matched | **16** |
| Original matched user VS outputs and FS inputs component lanes | **58** |
| Missing Fragment semantic records or lanes | **0 / 0** |
| Fragment component lanes absent from matched Vertex output | **0** |
| Matched semantic component-type mismatches | **0** |
| Original unused Vertex user semantic outputs | **0** |
| Source pairs with complete user semantic/type/mask VS→FS link | **4 / 4** |
| Original compiled semantics→derived HLSL/SPIR-V Location link verified | **NO** |
| Android GPU/Unity native ShaderLab visuals verified | **NO** |

**Meaning:** The four original PC DXBC variants were compiled with internally consistent authored user-interpolator semantics, type classes and component masks. In contrast, previous real [CI42144978122](https://github.com/alwansan/raf/actions/runs/42144978122) showed original-vs-HLSL-roundtrip compiler-reflected SPIR-V names disjoint **0/46**, while [CI42141506120](https://github.com/alwansan/raf/actions/runs/42141506120) showed original pair SPIR-V interfaces 4/4 compatible and roundtrip 2/4. The remaining problem is to **recover the original semantic/register/location mapping through the translation pipeline**, rather than guessing by a renamed compiler variable or a copied location index.

## New code, controls, scope boundaries

- New `scripts/t3_original_particle108_dxbc_semantic_join.py`: exact original SHA selected private Particle108 identity and genuine four paired DXBC buffers, delegates all DXBC chunk/signature decoding and per-pair semantic/component comparison to already-reviewed T3 original top921 helper, aggregates numeric allowlist; no authored semantic names, source registers, bytecode, hashed names, IDs, GUIDs, stage details or artifacts exported.
- New `tests/test_t3_original_particle108_dxbc_semantic_join.py`: six source-free tests for complete signatures, missing Fragment authored semantic, short Vertex mask, different component types, injected private comparator metadata, malformed original chunks and 4-pair byte bounds. All inherited 141 existing tests also passed.
- Isolated `.github/workflows/raft-t3-original-renderer-shader-impact.yml` source-only workflow. No `.shader`, `.meta`, original Texture, Material, prefab, scene, sound, Settings, input, water/FFT, saved world, signed native APK/OBB or original bytecode modified. No other client's CI cancelled.

## Follow-up engineering acceptance

Compare the original ISGN/OSGN authored semantic+register+mask evidence privately with vkd3d-generated source SPIR-V locations and **HLSL `SV_*`/`TEXCOORD*` semantic declarations**. Require an unambiguous one-to-one source semantic→source Location→HLSL field/register correspondence across each of four source keyword permutations. Handle system values like position and duplicate typed user varyings explicitly; if unproved, report BLOCKED rather than editing ShaderLab. Preserve the original ColorMask RGB / alpha Blend / ZWrite OFF and ten authentic Material Texture pointers. Only if all four roundtrip VS/FS pairs pass strict exact semantic correspondence plus Vulkan validator, consider a disposable ShaderLab candidate and T5 full native/Adreno phone fire/smoke tests.

**Gate: RENDER-002 OPEN / NOT_READY, source-only proof.**
