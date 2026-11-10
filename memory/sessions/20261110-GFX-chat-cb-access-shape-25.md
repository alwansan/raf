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
