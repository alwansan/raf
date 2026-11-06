# T3 → T5 / scheduled T3: real original Particle108 compiler-reflected names 0/46 preserved; do NOT patch locations by names

[CI42144978122](https://github.com/alwansan/raf/actions/runs/42144978122) SUCCESS **141/141** source-free/adversarial tests plus real SHA-original six-scene/four Shader owner source. On exact 108-use Particle Shader48 four true original DXBC VS/FS keyword pairs, all 8 stages generated Vulkan1.1 SPIR-V/HLSL/roundtrip. Source VS/FS interfaces 4/4 compatible but roundtrip only 2/4.

Private `spirv-cross --reflect` compared *full compiler names* between original Vulkan SPIR-V and SPIRV-Cross HLSL→glslang SPIR-V. ALL located source input and output names are renamed in derivative: **0/26 input and 0/20 output name+type matches**, **0/8** complete stage name identity, **0/2** mismatched variants with complete name bridge. Input/output location counts and type multisets survive (CI42141506120), but identical type does not identify semantic correspondence when names differ. No auto location patch should be applied by reflected names, sorted location or type-only guesses.

Next: original DXBC semantic signature (ISGN, OSGN, SGN extensions) and reconstructed HLSL SV_*/TEXCOORD* declarations must provide authenticated one-to-one semantic→register→location mapping for four keyword variants. If ambiguous, mark BLOCKED. Preserve ColorMask RGB, alpha Blend, ZWrite OFF and 10/10 original Material texture pointers. T5 should independently check exact source Shader GUID after native vendor restorers and identify real installed Android square fire/smoke emitter. No production `.shader`/`.meta` or APK changed.

Scheduled T3 reflection-order fix commit 42a77991812983a9d2f682640b73d096badbcba6 was left untouched, and this CI's inherited tests exercised it successfully.

Report https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE108_REFLECTED_NAME_MAPPING_2026-11-06.md
Resource https://github.com/alwansan/raf/blob/feature/android-native-port/prompt/coordination/B_TEAM/resources/T3-original-particle108-authentic-D3D11-variants.json
