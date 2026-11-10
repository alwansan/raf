# GFX-LAB — 20261110-GFX-chat-unreferenced-shader48-06
- session_id: `20261110-GFX-chat-unreferenced-shader48-06`; origin: `chat`; resumed_from: `20261110-GFX-chat-owner-autolog-matrix-05`
- base_sha: `cd77afba3d1378564cbc22bde285dd9534c8d59e`
- experiment_key: `GFX-MULTI-032`; issue: RENDER-002; resource_key: `gfxlab-multi032-source-private`
- source SHA: `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- status: IMPLEMENTING
## Scope
Examine only the compiled Shader48 programs in the source table not addressed by any authentic linked stage row, correcting the evidence gap after GFX-MULTI-022 (1,275 unique referenced out of 1,656 total). For each unused program perform bounded DXBC container/RDEF checks and publish aggregate count only, no user source, shader, IDs, texture or buffer bytes. No original Android ShaderLab APK until material→resource/CB bridge, dynamic pass states and pixel parity proven.
## Negative controls
Even if RDEF is present in an **unreferenced** program, it does not prove that a selected pass or original Shader48 material links to that program. No speculative source b/t/s offsets. T-team and all other branches read-only.
## CI / result
Pending original-source private CI.

## GFX-MULTI-032 implementation
- source checker: `gfxlab/tools/multi_shader_unreferenced_reflection.py`; fail-closed 1,656 compiled entries, 1,435 original variant links, 1,275 unique referenced indices, 381 unreferenced entries. Fails if source topology/counts/types shift.
- bounded original DXBC RDEF parse only for unreferenced DX11 entries; emits counts, never raw names/bytes/identifiers.
- source-free synthetic tests: `gfxlab/tests/test_multi_shader_unreferenced_reflection.py`, including ambiguous DXBC rejection and unbounded-code guard.
- private workflow: `.github/workflows/gfxlab-multi-unreferenced-rdef-source.yml`; pinned ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, sparse checkout, private source purge on success/failure.
- [CI42807637443](https://github.com/alwansan/raf/actions/runs/42807637443) started at `c29391f1cdc5357e147bf0f84a9108f7ad909e50`. **Result pending at this written checkpoint**. Do not report shader phase completion or create a new original Shader48 APK.

## GFX-MULTI-032 confirmed terminal outcome (2026-11-10)
- [CI42807637443](https://github.com/alwansan/raf/actions/runs/42807637443) COMPLETED **SUCCESS**, **198 source-free unit tests** (includes five new test cases), original ZIP2 SHA pinned.
- All 1,656 compiled programs accounted; 1,275 unique referenced (original 1,435 linked records, 524 keyword/tier VS-FS pairs), **381 unreferenced**. Among unreferenced **112 empty-code**, **269 non-DX11 typed** with data, **0 additional DX11 valid DXBC**, thus **0 RDEF candidate** in unused entries. All 1,275 linked genuine DX11 programs were already RDEF-absent from GFX022.
- Safe count artifact [13759565415](https://github.com/alwansan/raf/actions/runs/42807637443/artifacts/13759565415) expires 2026-11-17T11:28:16Z. Runner printed `GFX_MULTI032_PRIVATE_SOURCE_PURGED=true`. No original Shader48 source binary, identifiers or owner files committed.
- The 269 non-DX11 typed table entries **are not linked to original Shader48 Passes**; their type alone is not proof of Android GLES shader or a Material register mapping. Investigate only as separately bounded source candidates; original program/property bridge still BLOCKED.
- Evidence level ORIGINAL_SOURCE only; `originalShaderRestored=false`, `originalMaterialToDX11RegisterOffsetsVerified=false`, `phase_closed=false`. No Unity/GLES or game APK from this experiment.
- Next: GFX-MULTI-033 bounded classification of unlinked non-DX11 program **format** and direct pass-link feasibility, or independent original PC ShaderLab/RenderDoc material/CB evidence to resolve missing source reflection.
