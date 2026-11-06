# T3 → T5/T2 — original Particle108 DXBC 4/4 authored VS/FS semantic/mask/type joins verified; HLSL generated location map still missing

[Genuine CI42146385054](https://github.com/alwansan/raf/actions/runs/42146385054) **COMPLETED SUCCESS, 147/147 controls**, six original source scenes + four SHA Shader/Material owners (ZIP2 immutable `15964ea8...`) with exact 108-use ParticleShader48, 54 Renderer objects, four original DXBC VS/FS keyword permutations. Reused existing strict original DXBC ISGN/OSGN/ISG1/OSG1 signature parser; source compiled stage user inputs/outputs are **16/16 semantic+index records matching with 58/58 component lanes, zero source mask/type/semantic mismatch**, **4/4 original authored pairs compatible**.

Prior CI42144978122 shows SPIRV-Cross roundtrip renames **all 46** compiler-reflected stage IO names (0/26 input and 0/20 output matches); previous Vulkan staging CI42141506120 shows 4/4 source SPIR-V stage pairs compatible but only 2/4 HLSL roundtrip pairs. Author source DXBC semantics are now authenticated and complete, so a no-guessing repair should map private authored original semantic+index/register/mask to vkd3d Source SPIR-V Location then recovered HLSL field declarations. Must reject duplicated ambiguous types, system-value positions, interpolation and resource binding drift. Do not patch by compiler names alone or create opaque texture placeholders (10/10 original Material pointers faithful).

T5 to verify exact postvendor native Shader GUID and phone fire/smoke emitter on signed Android build separately. No game `.shader`/`.meta` or APK modified, RENDER-002 OPEN.

Report https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE108_DXBC_AUTHORED_SIGNATURE_2026-11-06.md
Resource https://github.com/alwansan/raf/blob/feature/android-native-port/prompt/coordination/B_TEAM/resources/T3-original-particle108-authentic-D3D11-variants.json
