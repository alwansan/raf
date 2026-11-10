# GFX-LAB — 20261110-GFX-chat-glsl-embedded-markers-09
- session_id: `20261110-GFX-chat-glsl-embedded-markers-09`; origin=`chat`; resumed_from=`20261110-GFX-chat-glsl-source-evidence-08`; base_sha=`e375d3c764c07b50c7bf6e61ed950755d86ccb16`
- issue RENDER-002; experiment_key `GFX-MULTI-035`; source ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- status: IN_PROGRESS.
## Scope
Search 139 original unlinked GLES and 120 GLCore compiled `m_ProgramCode` sources for **bounded binary byte-level** GLSL markers, exact authored Shader48 property-token presence and true UTF8-like printable text spans. No decode-only assumptions; no raw source or IDs in Git.
## Limits
Neither a generic compiler family nor a GLSL-looking substring proves an authentic original 7-Pass/524-variant link, Material→register offsets or Android GLES GPU parity. If no verified source mapping, preserve `originalShaderRestored=false`. No full game build or modifications to T-team branches.
## Runs
Pending.

## Implementation checkpoint
- Created `gfxlab/tools/multi_shader_glsl_embedded_markers.py`, strict bounded binary-marker scan; `gfxlab/tests/test_multi_shader_glsl_embedded_markers.py`, source-free fixtures; and `.github/workflows/gfxlab-multi-glsl-embedded-markers.yml`, independent private ZIP2 source job with mandatory purge.
- Tests inspect generic ASCII `#version`, `void main`, `uniform`, sampler, long printable text windows, exact source property-token boundaries including three bound material property roles. Only aggregate counts and marker offset bins may be exported; source shaders/ids/names remain in runner.
- [CI42810629895](https://github.com/alwansan/raf/actions/runs/42810629895) source-free unit tests **SUCCESS**, authenticated ZIP2 inspection running at this checkpoint. Original Shader48 GLSL, CB/sampler semantics, Pass linkage, Adreno pixels remain unproven.

## GFX-MULTI-035 verified terminal outcome (2026-11-10)
- [GFX-MULTI-035 CI42810629895](https://github.com/alwansan/raf/actions/runs/42810629895) **COMPLETED SUCCESS, 216 Python tests**, pinned original ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; private source purge passed. Among **139** unlinked GLES programs: **82** contain exact original Shader48 authored property byte tokens, **76** contain original bound material tokens; 14 distinct authored labels, 5 distinct texture labels, **all 3 bound material property labels**. Among **120** unlinked GLCore programs: **61** have authored property tokens, **60** have bound material tokens; same 14 authored /5 texture /3 bound distinct labels. **ZERO** `#version`, `void main`, `uniform`, sampler markers or 32-byte contiguous printable ASCII windows in either family; **zero** matched bound property tokens within uniform declarations. Embedded NUL in GLES 115/139 and GLCore 106/120. Thus binary payloads contain property-name tokens but **not verified plain GLSL or uniform binding**. No source Pass/keyword/tier link, Material→DX11 register/CB offsets, Android original shader runtime, PC pixel parity. Safe artifact [13762103464](https://github.com/alwansan/raf/actions/runs/42810629895/artifacts/13762103464) expires 2026-11-17T11:51:10Z; no original assets uploaded.
- Next source-only experiment GFX-MULTI-036 may examine documented Unity GL binary **resource metadata layout**, but must fail closed on undocumented indices; request genuine original PC ShaderLab/reflection if no proof. No Android original Shader48 APK because G7–G12 remain blocked.
