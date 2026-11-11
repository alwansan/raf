# GFX145: Source-original Cull state preflight — 2026-11-11

GFX-LAB, origin=chat, sole write branch experiment/android-graphics-rootcause.

GFX144 proved that all M03-1 Adreno-vs-Mesa RGB outliers >10/255 lie at original double-faced coplanar opposite-normal/UV-identical triangle pairs, while both controlled renderers disable GL_CULL_FACE. The source original Shader48 Cull field is a named dynamic override, and GFX126 did NOT establish effective Unity runtime Cull state.

This new GFX145 source-pinned CI stage privately inspects all seven original Shader48 passes, the Cull enum fallback (`off`/`front`/`back`), original saved Material float override presence and valid enum mapping. Only enum categories, pass names, anonymized counts and explicit negative effective-runtime flags are exported. No original names, shaders, code, models or textures published.

Files: gfxlab/tools/gfx145_original_cull_gate.py, gfxlab/tests/test_gfx145_original_cull_gate.py, .github/workflows/gfxlab-multi145-source-cull.yml.

**CI PENDING at initial commit**. Inspect real run and artifacts before claiming a fallback enum or completing any state recovery. This test is not proof of the runtime Unity Cull state even with a valid fallback. Follow-up: controlled source original GLES cull off/front/back rendering and, if required, one focused Android test rather than a redundant complete 51-capture rerun. phase_closed=false.
