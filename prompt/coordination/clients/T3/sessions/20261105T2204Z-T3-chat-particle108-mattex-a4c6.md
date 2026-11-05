# T3 chat — original 108-use Particle Shader48 Material TexEnv PPtr source baseline

- **session_id:** `20261105T2204Z-T3-chat-particle108-mattex-a4c6`; **origin:** chat; **identity:** T3; **issue_id:** RENDER-002 OPEN / NOT_READY; **scope status:** completed.
- **resumed_from:** `20261105T214810Z-T3-chat-selective-colormask-a82d`; `20261105T213100Z-T3-scheduled-clstage-8b4f` (independent original CL log world vs water error timing).
- **base_sha:** `8b8519327c887b59893fca43a44d9a764fa639eb`; work registered **before edits** in `prompt/coordination/work/RENDER-002/20261105T2204Z-T3-chat-particle108-mattex-a4c6.json`, registration commit `3cf7c1e2971ab2d8b38c5cd57e0e2b24d6f1437d`.
- **experiment_key:** `T3-ZIP2-15964-6scene-4owner-source108-particleShader48-material-texenv-private-map-source-bound-v1`.
- **resource_key:** `t3-original-6scene-4owner-sourceonly-22min`, now released after terminal CI. No full native export/Unity build was launched.
- **edited files:** `scripts/t3_original_renderer_shader_impact.py`, `tests/test_t3_original_renderer_shader_impact.py`, `scripts/t3_original_particle_material_texenv.py`, `tests/test_t3_original_particle_material_texenv.py`, `.github/workflows/raft-t3-original-renderer-shader-impact.yml`, plus scoped work/session/experiment/event/doc/discussion records.

## Authenticated real original result

[Actions run 42119098398](https://github.com/alwansan/raf/actions/runs/42119098398) at exact code SHA `775a18ec59a061783d46e7fbb77125c0929c8d34` **COMPLETED SUCCESS**. Python compile and original source-free regression suites `23+13+7+5+11+22=81/81` PASS. Six immutable original Raft scenes plus four original owners verified SHA (269007288 total reassembled owner bytes) from ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` no LFS.

Private six-scene Renderer→Material→Shader48 graph selected the unique **108 ParticleRenderer Material-slot** Shader48 (54 distinct Renderer objects, one source Pass, ColorMask RGB/Alpha-dependent Blend from prior run), and through its private typed Shader48 source identity selected exactly **FIVE distinct source Material21 objects**. Those Materials expose **10 TexEnv slots**, **10 bound non-null Texture PPtrs**, **zero null**, **all 10 with m_FileID=0 local owner refs**, **three distinct scoped PPtr identities**, **all ten complete UV scale/offset**. These are original serialized Material pointers only: it does NOT prove source target type Texture2D, texture content, export GUID/link preservation, actual mobile sampler use, emitted phone particle or square-smoke cause.

Code: private materials map `05d460d6853397ce6df765a435f21fbe4930435c`, SHA source analyzer `02bdaba315805fe48684faafdeedf2a692725f16`, seven negative synthetic TexEnv tests `e812e6f1f6779d819c2c1511ea80917b5680d8d7`, two in-memory outparam tests `37c2e13eb28c548f3db5713147c9e8ee63bc57cf`, bounded real CI workflow `775a18ec59a061783d46e7fbb77125c0929c8d34`. Only safe numeric aggregates published; shader/Material IDs, property labels, original game bytes never leave runner. T1 water Vulkan job was in progress when we ran this source-only scope; no cancellation or overlap.

**Detailed report:** https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE108_MATERIAL_TEXENV_2026-11-05.md

## Next / handoff

Compare the exact 5 SHA-original ParticleShader48 Material21 objects and their 10 non-null local Texture PPtrs / 3 unique source targets with *same-instance* W1 Material21/B02 Texture2D28 export trace and current Android-installed shader/texture GUID bindings. Check Texture2D object type/metadata before claiming source texture payload presence. Match phone emitter prefab/material and fire/smoke pixels before changing game shaders.

Do not silently substitute a known-looking public shader, remove alpha, switch ColorMask RGB to RGBA, or declare RENDER-002 READY based on material slots. No game source/ShaderLab/.meta/GUID/audio/Settings/input/local-save/assets/Unity build changed. Separate scheduled T3 sessions and old state/MEMORY not overwritten.
