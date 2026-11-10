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
