# 20261110-GFX-chat-shader-gles-stage-io-12
- session_id: 20261110-GFX-chat-shader-gles-stage-io-12; origin: chat
- resumed_from: 20261110-GFX-chat-shader-pass-pair-spirv-11
- base_sha: 521e555a7ae9330bd1d63e650290e0b81874fafc
- experiment_key: GFX-MULTI-012-exact-one-pass-original-SPIRV-interface-and-GLSL-ES310-offline
- scope: original shader exact VS+FS keyword/tier matched pair, SPIRV-Cross reflection and GLSL ES 3.10 syntax check inside ephemeral runner; no game/Android build
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- prior_run: GFX-MULTI-011 CI42731898965 SUCCESS. 65 unit tests; authentic source DXBC VS+FS, exact keyword and player bucket match; both CPU translations vkd3d -> Vulkan1.1 SPIRV PASS and spirv-val PASS. Source 7 of 7 passes have >=1 exact stage pair (counts 80,156,32,80,40,120,16; total524). No source bytes/public shader exports. Original AndroidShader restored FALSE.
- proposed CI: GFX-MULTI-012 source-only, reflection VS output vs FS input locations/types, GLES310 source generation + offline glslangValidator syntax. This does not prove interpolation, binding, Unity GLES3 runtime or pixels.
