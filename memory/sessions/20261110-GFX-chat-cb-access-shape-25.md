# GFX-LAB 20261110-GFX-chat-cb-access-shape-25
- session_id: `20261110-GFX-chat-cb-access-shape-25`; origin: `chat`; resumed_from `20261110-GFX-chat-cb-dcl-spv-byte-sizes-24`.
- base_sha: `a14d3c8186755760fb70e5fcb59aa39f2a06c67d`; only write `experiment/android-graphics-rootcause`; original ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- experiment_key `GFX-MULTI-051`; issue `RENDER-002`; scope: original source CB use / SPV UBO candidate access profile (not offsets proof).
- Baseline GFX050 [CI42843665847](https://github.com/alwansan/raf/actions/runs/42843665847) 341 tests; 66/66 numeric b# / UBO block-byte-size candidates, **0 original-name-authenticated CB identities**.
## Method / negative controls
- For exactly one keyword/tier paired original DXBC VS/FS per Shader48 Pass (14 programs), scan **only** nine bounded known fixed-arity arithmetic DXBC instruction opcodes for source CB operands; distinguish literal vec4 b# indices from dynamic or extension operands, malformed instructions and unsupported other opcodes.
- For same translated SPIR-V Vulkan1.1 program, inspect explicit UBO reflected member offsets / strides and real `OpAccessChain` / `OpLoad` candidate-use paths at numeric set0/binding. Privately compute conservative overlap of literal vec4 indices in covered DXBC subset and SPV candidate paths. No public register indices, member offsets, shaders, data, names or signatures.
- Fail closed on opcode truncation, source index OOB, duplicate SPV decorations. Track remaining unsupported instructions and unknown indices. The numeric binding is provisional only; source CB register identity and member layout are **not** proven by matching byte totals or access-index candidates.
- Workflow `.github/workflows/gfxlab-multi051-cb-access-shapes.yml`; tool `gfxlab/tools/multi_shader_original_cb_access_shapes.py`; tests `gfxlab/tests/test_multi_shader_original_cb_access_shapes.py`.
- CI pending, do not infer success. No game/Unity build or mobile APK, untouched T1–T5.
## Limits
- Evidence level ORIGINAL_SOURCE plus SPIR-V CPU-only structural use-shape. Source scan is **partial** by opcode family; no full CB member byte mapping, genuine ShaderLab property bindings, independent CB identity, Android GPU runtime or PC↔Adreno pixel parity. `originalShaderRestored=false`.

## Final source-private CI evidence
- [CI42845677322](https://github.com/alwansan/raf/actions/runs/42845677322) SUCCESS, 350 synthetic unit tests, 14 original source stages (7 genuine keyword/tier VS/FS pairs), ZIP2 SHA pinned, runner original source/translated SPIR-V purge verified.
- 776 original fixed-arity arithmetic instructions decoded in nine families (partial), 0 rejected recognized parser shapes; 290 static source CB vec4 operand occurrences, 208 distinct source b#/vec4 locations by stage, 27 dynamic/extended source operand access shapes unresolved.
- vkd3d Vulkan1.1 SPIR-V: 445 UBO numeric-binding candidate access chains, 344 literal vector candidate chains, 344 pointer loads. All 208 known source subset distinct b#/vec4 locations overlap with SPV literal candidates at numeric coordinates; 20 SPV-only literal candidate locations vs limited source opcode subset. 66 reflected UBO member offset+array stride16 records. All 14 source stages have same-numeric source b#/UBO block byte size candidates.
- **No** authentic CB source register identity from UBO names, exact member byte-offset map, whole original DXBC opcode use coverage, real Shader48 GPU proof, or original PC pixels. G8 still blocked, `originalShaderRestored=false`.
- [Safe artifact 13779226051](https://github.com/alwansan/raf/actions/runs/42845677322/artifacts/13779226051), expires 2026-11-17T15:34:57Z. Private b#, vec4, shader bytes and UBO offset values not published.
- Outcome: SUCCESS_BOUNDED_SOURCE_CB_VECTOR_USE_TO_SPV_NUMERIC_ACCESS_CANDIDATES_NOT_SEMANTIC_IDENTITY. Next GFX052 authenticate SPV actual UBO global `OpName` independently from SPIRV-Cross block names, or prove no symbol bridge.
