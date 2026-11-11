# 20261111-GFX-chat-original-spirv-interpolation-72 — GFX103 lexical hardening + GFX104 source private DXBC → SPIR-V → GLES310 bridge

**role:** GFX-LAB · **origin:** chat · **write branch:** `experiment/android-graphics-rootcause` · **resume:** `20261111-GFX-chat-owner-gfx102-native-noperspective-71`

## Ground truth and why this step matters
- Actual owner GFX102 phone proof **native noperspective on Adreno 730**: GLSL ES 310 and 320 compile/link and real GPU output is byte-identical to affine-emulated reference, while ES300 native rejects reserved keyword. This proves a synthetic shader on the owner's GLES driver; does **not** prove original Shader48 pixel parity.
- Historical GFX039 source aggregation: 16 `linear_noperspective` declarations **and** 16 `DCL_INPUT_PS_SIV` declarations across 655 distinct original PS programs. The two counts might overlap; GFX103 distinguishes normal `DCL_INPUT_PS` from system interpreted `DCL_INPUT_PS_SIV` for 524 exact runtime pairs. Do not assert original standard varyings need native qualifier before source-safe execution returns.
- Official SPIR-V spec (https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html): `OpDecorate` opcode71; `OpMemberDecorate` opcode72; `NoPerspective` decoration13; `BuiltIn` decoration11; `Flat` decoration14. GFX104 reports **candidate** decorations, not original register identity. Built-in decorated members are excluded from ordinary-input NoPerspective counts.

## Changes committed in this cycle
- **GFX103 fix:** `gfxlab/tools/gfx103_source_interpolation_gate.py` now lexically excludes GLSL comments and quoted strings before looking for native interpolation and recognises both `noperspective centroid in` and `centroid noperspective in`, likewise `sample`. Additional source-free regression cases in `gfxlab/tests/test_gfx103_source_interpolation_gate.py`. False comment evidence previously could incorrectly pass the native proof gate.
- **GFX104 parser:** `gfxlab/tools/gfx104_spirv_input_interpolation.py`, bounded SPIR-V 32-bit instruction parser, counts direct ordinary NoPerspective, builtin and member NoPerspective separately; grouped decorations or unresolved pointer types remain explicit inconclusive flags. Never exports SPIR-V IDs/variables or original game shader text.
- **Private source runner:** `gfxlab/tools/gfx104_source_shader_spirv_bridge.py` walks all 524 exact original Shader48 source pairs in ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, translates only distinct original PS programs with source NP declarations to SPIR-V and GLES ES310 via existing vkd3d/SPIRV-Cross tools. Reports only bounded safe aggregate counts, no raw source or shaders.
- **Tests:** `gfxlab/tests/test_gfx104_spirv_input_interpolation.py` (9 new synthetic tests), `gfxlab/tests/test_gfx104_source_shader_spirv_bridge.py` (5 mocked source/private tests). Source-free isolated local mirror: 6/6 synthetic SPIR-V tests and six GLSL qualifier lexer examples passed. **Do not call full CI verified from local mirror.**
- **Workflow:** `https://github.com/alwansan/raf/actions/workflows/gfxlab-multi104-source-spirv-native-bridge.yml` checks tests, downloads exact source inside the private runner, translates affected programs, publishes only aggregated JSON, and purges private source even on failures. GFX103 existing workflow at `https://github.com/alwansan/raf/actions/workflows/gfxlab-multi103-source-interpolation-classes.yml`.

## Critical truth and next owner/assistant actions
1. **Cannot independently confirm terminal Actions outcomes or artifact IDs in this chat.** Github connector can fetch commit files, but the supplied workflow search action is limited to PR-triggered runs; no current GFX103/GFX104 push-run ID. Need actual terminal SUCCESS and safe JSON, not inferred counts.
2. GFX103 must prove original PS ordinary/SIV split for the exact 524 pairs; GFX104 must test whether original DXBC NP becomes SPIR-V NoPerspective (or builtin) and whether GLSL310 source has correct native qualifier. Even a source-side CPU validation is not device pixel parity.
3. Next if any ordinary varying is affected: isolate its exact shader pair for a **driver** compile/link/pixel experiment with original parameters after material/CB binding is authenticated. Avoid blending with synthetic evidence or claiming all Shader48 restored.
4. Keep original texture/sampler/constant buffer identity, rig/animation, full original shader variants, original Windows vs Adreno pixel parity open. No further phone APK is required for these *source-private CPU gates* at present.

**Flags:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `sourceMaterialRegisterBindingVerified=false`, `pcAdrenoPixelParityVerified=false`, `phase_closed=false`.

