# T3 — authentic original high-use Shader48 D3D11 pass/variant feasibility (2026-11-05)

**Worker:** T3; chat session `20261105T143219Z-T3-chat-original921-builtin-2f7b`; issue **RENDER-002 OPEN**. All data described here are **serialized original-source** and CPU-only, **not** Android shader restoration or a playable game build.

## Why the targeted original Shader matters

Authenticated six-scene original Renderer Material-slot graph [42042819113](https://github.com/alwansan/raf/actions/runs/42042819113) identified 21 typed Shader48 targets across 1,633 original Renderer material slots. The most-used original Shader48 target has **921 slot references** in these six original scenes. Authenticated same-instance source Shader48 → exported GUID → actual post-TMP/PostFX/Volumetric shader audit [42044249541](https://github.com/alwansan/raf/actions/runs/42044249541) proved this high-use source target still has an AssetRipper Dummy-marked ShaderLab file after those three restorers. Independently, [42046329453](https://github.com/alwansan/raf/actions/runs/42046329453) **SUCCESS** proved this top Shader's serialized source name is **not** in the 198 exact SHA-authenticated Unity 2021.3.45f2 built-in runtime Shader names. Therefore an exact official-builtin name replacement is **not** an evidenced restoration route for the 921-use source target.

**Do not conflate** original Renderer slot count, default exported Material documents, actual visible white objects or GPU draw calls.

## New original D3D11 source experiment

[CI42047611046](https://github.com/alwansan/raf/actions/runs/42047611046) **SUCCESS** on `71276a55afc165102852def8b84ea21995c3ca53`, using source-only `scripts/t3_original_top_shader_dxbc_feasibility.py` and tests `tests/test_t3_original_top_shader_dxbc_feasibility.py`. The isolated workflow assembled **four SHA-verified original Shader/Material owners, 269,007,288 bytes in total, plus six SHA-verified level0–level5 scenes**, all read from immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. UnityPy 1.23.0 selected the authentic high-use original Shader48 by **source Renderer→Material→Shader identity**, never by a guessed Shader name/GUID.

The experiment decoded the original Shader object's compressed platform segments and required exactly one D3D11 platform table, indexed serialized blob records with validated segment-relative bounds, and read each normal Pass's original `progVertex` and `progFragment` player/editor stage variant metadata. For every variant, it invoked the existing strict `linked_program` guard, which verifies a single genuine DXBC container and the correct original vertex/fragment bytecode stage. Exact variant pairing used the original hardware tier and keyword permutation metadata. **No raw stage program, original shader name, original path/GUID/serialized IDs, blob bytes, or per-program hash were published.**

| Source-authentic observation | Verified count |
| --- | ---: |
| Source Renderer Material slots referencing selected Shader48 | **921** |
| Original Shader48 SubShaders | **1** |
| Original Passes | **4** |
| Original normal Passes | **4** |
| Original non-normal Passes | 0 |
| Actual D3D11 program-table entries | **120** |
| D3D11 vertex variant stage records linked | **41** |
| D3D11 fragment variant stage records linked | **33** |
| Distinct original linked D3D11 compiled program contents, private hash set | **58** |
| Exact vertex/fragment permutation matches | **33** |
| Normal Passes with at least one exact paired permutation | **4 of 4** |
| Unmatched vertex permutations | **8** |
| Unmatched fragment permutations | **0** |
| Stage-variant records containing source keyword permutations | **72** |

**Interpretation:** original D3D11 compiled stage programs and linked per-Pass variant metadata are present and recoverable *as source evidence*. All four Passes have at least one exact original vertex/fragment permutation pairing, but eight vertex permutations remain unmatched and cannot be silently discarded or forced to fragment slot zero. Stage source can guide a real ShaderLab port only after pass states, resource binding/CB/samplers, authored keyword/variant coverage, DXBC translation and actual Unity Android compilation are verified. D3D11 compiled programs are **not** Unity Android GPU shaders.

## Negative controls and scope

In [CI42047611046](https://github.com/alwansan/raf/actions/runs/42047611046), **12 new D3D11 stage/variant tests, 12 inherited T3 original Renderer graph tests and 22 inherited B03 tests passed = 46 source-free tests**, followed by the actual original-stage proof. The tests reject forged original population, duplicate/missing top-weight identity, wrong shader stage, missing Fragment program, nonempty bad variant metadata, duplicate permutation, absent stage code and report identifier leakage. Non-normal Passes remain explicitly non-linked. Python syntax checks passed.

The predecessor [CI42047453578](https://github.com/alwansan/raf/actions/runs/42047453578) **FAILED in a synthetic privacy test**: the test rejected an ordinary public report field containing the generic word `private`, not a genuine source leak or original shader problem. Corrected the fixture to use one unique synthetic secret sentinel at commit `71276a55`; no actual Raft asset stage ran in that failed CI.

Separate builtin-name experiment introduced during this chat [CI42046452052](https://github.com/alwansan/raf/actions/runs/42046452052) **FAILED as INCONCLUSIVE** in original-source comparison; it must not be used as authenticated evidence. The independent successful earlier builtin-name result [CI42046329453](https://github.com/alwansan/raf/actions/runs/42046329453) is authoritative. Both expensive T3 workflows were made **manual-only** after the decisive evidence to prevent duplicate original ZIP2 experiments. The duplicate builtin-name code did not change any original game shader/GUID.

The scope excludes other Shader48 programs, full original 40 scenes, complete pass state/CB/texture/Sampler reflection, code translation, original shader source comments, vendor source equivalence, later native full project restorers, Unity 2021 Android imports, Vulkan/Adreno pixels, world gameplay and saved `.rgd` files.

## Next engineering action

Using exact original D3D11 data that now has validated stage linkage, begin a **private bounded four-Pass reconstruction** for the selected high-use shader: preserve the actual original Pass order, SubShader render state, source keywords and vertex/fragment pairing; analyze the **eight extra Vertex permutations** instead of fabricating missing Fragment variants. Translate selected matched original DXBC pairs privately to SPIR-V/HLSL with vkd3d-compiler, spirv-val, SPIRV-Cross and glslang, then validate resource bindings and Unity ShaderLab without publishing proprietary source, bytecode or unverified synthetic fallback Passes. Only after authentic per-Pass evidence should restored source be staged under original exported shader GUIDs with Unity Android/device visual acceptance and team coordination.

**RENDER-002 remains OPEN; no game asset, .shader, .meta, Unity prefab/scene, APK/OBB/XAPK, sound/Settings or touch change by this diagnostic.**
