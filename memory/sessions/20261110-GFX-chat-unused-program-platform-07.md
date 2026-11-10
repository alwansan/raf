# GFX-LAB — 20261110-GFX-chat-unused-program-platform-07
- session_id: `20261110-GFX-chat-unused-program-platform-07`; origin=`chat`; resumed_from=`20261110-GFX-chat-unreferenced-shader48-06`
- base_sha: `7e0e01c13bae9e331004a4e90efbce5233f5a9cb`
- source ZIP2 SHA: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- experiment_key: `GFX-MULTI-033`, issue RENDER-002, resource_key gfxlab-multi033-source-private
- status: IN_PROGRESS
## Scope
Enumerate **269 non-DX11 typed nonempty programs** not linked by 1435 stage variants, identifying only generic ShaderProgramType platform and stage categories, not original program name/value/text. Explicitly distinguish type label candidate vs bounded code container signature and authentic original Pass↔stage↔variant linkage. Look for extra `prog*` original Pass fields outside VS/FS; do not guess compiled table positions.
## Negative controls
Unreferenced code cannot prove original Shader48 GLES/Vulkan execution on Adreno. Original Material property→DX11 t/s/CB and render-state mapping missing; no original PC pixel capture. No artifact containing original DXBC/GLSL/SPIR-V. Do not touch T branches, main, zip2 or release game APK.
## Runs and results
Await private source CI. After terminal result update this session, RESTORE_AR, OPEN_WORK_AND_IDEAS, MEMORY, STATE and verify HEAD.

## Implemented source experiment and active CI
- Created `gfxlab/tools/multi_shader_unused_program_families.py`, source-free contract `gfxlab/tests/test_multi_shader_unused_program_families.py`, and independent `.github/workflows/gfxlab-multi-unused-platform-census.yml`.
- Generic program type families D3D9/D3D11/GLES/GLCore/Vulkan/Metal/Console/Other and stage family categories; strict *leading* GLSL/SPIR-V/DXBC signatures only, unknown remains unknown. Checks all 381 unlinked entries with 112 empty+269 non-D3D11 anchored to GFX032.
- Inspects alternative original `prog*` Pass stage metadata fields with exact original type/compiled index comparisons; no program-name or byte export.
- Source-free regression passed in [CI42808967835](https://github.com/alwansan/raf/actions/runs/42808967835) at `6c1771cf468678c56687d3fe4cb2dc06c87c0bcf`. **Original-source stage still in progress at this checkpoint.** Do not treat type family/leading header as a verified Shader48 Android runtime.
