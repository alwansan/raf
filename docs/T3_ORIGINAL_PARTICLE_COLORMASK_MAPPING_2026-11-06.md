# T3 — Unity 2021.3 ColorWriteMask bit fidelity for original Raft Particle Shader48

**Result: source-only targeted translator fix verified. RENDER-002 remains OPEN / NOT_READY; no Android pixels, full native shader equivalence or fire/smoke acceptance.**

## Proven Unity-specific bit order

- UnityCsReference **2021.3** branch, `Runtime/Export/Graphics/GraphicsEnums.cs`, blob `855eebe69c60dcaea85a74d91656fc02df43ea90`: `[Flags] ColorWriteMask { Alpha=1, Blue=2, Green=4, Red=8, All=15 }`.
- Official Unity 2021.3 ShaderLab `ColorMask` accepts channel letter subsets. See https://docs.unity.cn/2021.3/Documentation/Manual/SL-ColorMask.html and https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs.
- **Do not** use the widely seen opposite Red=1/Green=2/Blue=4/Alpha=8 bit order from other APIs. Here source mask **14 (8+4+2) maps to `ColorMask RGB`**, and mask 7 maps to `ColorMask GBA`. Full 15 maps to `RGBA`; 0 maps to `0`. Unity 2021.3 manual's textual description for `ColorMask 0` is inconsistent with the command's established disabled-write semantics; the translator preserves the existing `0` behavior.

## Authentic original source verdict

- [Actions run 42116530618](https://github.com/alwansan/raf/actions/runs/42116530618) completed **SUCCESS** at SHA `d6926a0bbd862cf3a8af0fd6ee0b5da018bdaf2d`. Source-free Python suite counts **21 original Renderer + 13 Particle-state + 5 W1 Depth ShaderLab + 11 B25 Foam pass-state + 22 B03 original Renderer = 72/72 PASS**. All original six scenes and four Shader/Material owners verified against ZIP2 pinned commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, 269007288 owner bytes, no LFS.
- Source identifies the unique highest ParticleSystemRenderer Shader48 privately from real original Renderer→Material→Shader48 PPtrs, 108 material slots, 54 distinct renderers, one normal original Pass, zero nonparticle slots.
- The original one-Pass `ColorMask` is exactly **RGB**, not RGBA. Original Color Blend and Alpha-channel Blend remain `ALPHA_DEPENDENT`, `ZWrite OFF`, `Cull OFF`, alpha-to-coverage `OFF`, depth testing enabled.
- Original `render_state(state)` default **rejects** this selective mask, same as before. Opt-in `render_state(state, allow_selective_color_mask=True)` **accepts** its entire original fixed-function RenderState without logging private ShaderLab text. This proves only the read-only fixed-function translator can represent the source state with mapped channels, not that emitted fragment outputs or Android rendering match.

## Implemented scope, safety, and regressions

- `scripts/w1_depth_shaderlab.py` adds `color_mask()` using the Unity2021 bit order, validates integer mask 0..15 and safe material property references; the shared default parser continues to accept only 0 or RGBA 15, preserving W1/B25 legacy fail-closed protection.
- `scripts/t3_original_particle_shader_state.py` tests default and explicit opt-in paths independently and reports only public-safe channel subset and acceptance flags; no original Material names, IDs, GUIDs or shader source escape.
- `tests/test_t3_original_particle_shader_state.py` tests all 16 masks plus malformed values, original source classification, dynamic property privacy and pass-state controls. The unchanged `tests/test_w1_depth_shaderlab.py` and `tests/test_b25_foam_pass_state.py` pass unchanged on the default path.
- The bound `.github/workflows/raft-t3-original-renderer-shader-impact.yml` runs all relevant unit suites and one SHA-authenticated six-scene/four-owner original reader. This is **not** a Unity native export or Android APK build.

## Next engineering gate

Prioritize same-instance original Shader48 → private W1 full-native exporter GUID / Material mapping of the 108-slot Particle Shader; check actual restored ShaderLab `ColorMask RGB` / alpha Blend + the real fragment shader/texture inputs, then reproduce fire/smoke pixels on the user's installed artifact. Source state alone is insufficient to assert that a specific emitter ran, that the dummy shader was replaced, or that any mobile shader now renders.

**No `.shader`, `.meta`, scene, prefab, texture, audio, Settings, save, touch/input, APK or OBB changed. No T1/T2/T4/T5 jobs cancelled.**
