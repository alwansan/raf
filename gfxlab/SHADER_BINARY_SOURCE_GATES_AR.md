# GFX-MULTI-010 — Original Shader48 binary-link verification
- Role: GFX-LAB; origin: chat; branch: experiment/android-graphics-rootcause; session_id: 20261110-GFX-chat-shader-binary-variant-links-10
- SOURCE ZIP2: 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- Previous proven GFX-MULTI-009 [CI42728348900](https://github.com/alwansan/raf/actions/runs/42728348900) completed SUCCESS with 59 tests. Reader reported one source compiler platform D3D11, 1,656 original compiled entries, mixed GPU-program type categories, 188 labelled GLES/GLES3/GLES31/AEP; all program content magic classified as other. Compressed source blob bytes=163,501; sum parsed program payload bytes=242,218,471. **Both the cross-platform category mix and size expansion require validation. They are not proof of GLES executables.**
- Research basis: UnityPy ShaderConverter reads Unity ShaderProgram.m_SubPrograms table from compressed LZ4 blob and stage entries referenced by original parsed pass m_PlayerSubPrograms/m_BlobIndex. This experiment verifies actual links and compiled-type agreement, plus safe content-family classifications. It never exports program code.
- Evidence ladder: source compressed program counts and typed variants SOURCE_ONLY. Unity Android original Shader48 compile, stage IO semantic, CB/samplers/keywords/render-state equivalence, GPU pixels, PC matching remain FALSE.
- User's phone visuals: Unity Standard diagnostic only; six models and image colors visible but original Shader48 NOT executed.

## GFX-MULTI-010 confirmed stage links
[CI42731206453](https://github.com/alwansan/raf/actions/runs/42731206453) SUCCESS: 1435 of 1435 original source stage variant links to compiled original programs valid, zero type mismatches, zero bad indexes; all referenced sources are DX11 with DXBC embedded signature, none of 188 generic table GLES-type records referenced by the 7 passes. Programs must be translated with exact stage semantics and keyword/tier pair; no assumption that 188 GLES metadata records run on Android. LZ4 decompressed length=4,338,048, aggregate program-content sum 242,218,471 (these are distinct measurements). No shader restored on Adreno.
## GFX-MULTI-011 source-only CPU pilot
Choose exactly matched original stage variant pair within one Pass and same original keyword+hardware tier player bucket; structurally verify two DXBC containers and try vkd3d-compiler translation to SPIR-V Vulkan1.1. This is only CPU feasibility, not Unity GLES3 ShaderLab, not original PC pixel parity and not rig restoration.


## GFX-MULTI-011 confirmation + next
[CI42731898965](https://github.com/alwansan/raf/actions/runs/42731898965): successful original DXBC VS/FS (same original keyword/hardware player tier) private vkd3d Vulkan1.1 SPIRV translation+validation for 2/2 stages. 524 exact matched stage pairs among 7 original passes (80,156,32,80,40,120,16), not 524 distinct shader programs necessarily. No private source leaked, no APK. GFX-MULTI-012 adds private SPIRV-Cross reflect/output-input location/type and GLSL ES 310 syntax gate. Original shader still open pending actual compiled Unity2021 Android GLES3, resource semantics, PC parity, owner acceptance.


## GFX-MULTI-012: actual source stage IO / offline GLSL ES
[CI42732370025](https://github.com/alwansan/raf/actions/runs/42732370025) proved one authentic source Shader48 VS and FS pair translates and compiles offline as GLSL ES310 (69 tests). SPIRV reflect 7 VS output locations match 7 FS input locations with equal types; 0 difference. Fragment resources 7 UBO+7 separate images+6 separate samplers; vertex 5 UBO. This does not prove original register/CB/sampler mappings, interpolation semantics or Adreno runtime. GFX-MULTI-013 extends to all seven original passes, one source-authenticated pair each. Do not call phase CLOSED from offline GLSL alone.

## GFX-MULTI-013: 7/7 pass representative source translation proof
[Run 42732808109](https://github.com/alwansan/raf/actions/runs/42732808109) SUCCESS: seven authentic Shader48 Passes each had one VS+FS source DXBC exact tier+keyword matched pair privately translated to valid Vulkan1.1 SPIR-V and valid offline GLSL ES 310 syntax. All reflected stage locations/types match; 0 missing fragment inputs or type mismatches. All 524 matched variants were NOT individually tested; resource bindings and authored render states are NOT verified; neither Unity Android compilation nor Adreno output is verified. Original Shader48 restored FALSE. All source bytes purged. **Do not claim full shader parity from 7/7 representative passes.**


## GFX-MULTI-016 SHA original SHDR declaration inventory
[CI42736745984](https://github.com/alwansan/raf/actions/runs/42736745984) source-only SUCCESS, 85 tests. All 14 original DXBC stage token streams (one matched pair per 7 Passes) parsed with strict Microsoft token length validation. Source declarations total: 66 CB, 29 resources, 27 samplers; 0 raw/structured; Pass0 VS5 CB, FS7 CB/7 resource/6 sampler matches reflected SPIRV resource **counts only**. No source register ids/offsets, constant packing, sampler texture binding equivalence or original GPU proof. All private code purged.
