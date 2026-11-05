# T3 → T5/T2: original top-921 Shader48 is a mesh shader, not a particle Renderer shader

From T3 source-only SHA-authenticated [run 42109994654](https://github.com/alwansan/raf/actions/runs/42109994654) on `3342cf6b1c996c2bcf7b7bf4d6caae23e3b7c29e`:
- Top original 921-use Shader48 = **914 MeshRenderer + 7 SkinnedMeshRenderer material slots, zero ParticleSystemRenderer**; same 914+7 distinct renderer objects
- Of six original scenes' 1639 total material slots: 1374 MeshRenderer, 46 SkinnedMeshRenderer, 219 ParticleSystemRenderer
- 1633 typed source Shader48 slots: 1372 Mesh, 46 Skinned, **215 ParticleSystemRenderer (OTHER shaders)**
- Tests 15+22 PASS, six scene/four owners SHA PASS. No original IDs/GUIDs/raw bytes were published.

Prior 110/142 full-native Dummy scanner and top source 921 Dummy in bounded vendor export still need **true same-instance private original→full-native W1 trace**; no inference that top921 is one of 110 full-native dummies. For white raft/hand focus authored 4-pass mesh ShaderLab/variants; for square smoke/fire focus other original ParticleSystemRenderer shader ranks and actual alpha/texture/blend. No native test/rebuild requested, no T1/T2/T5 job touched; audio, Settings and input unchanged.

Session `20261105T210656Z-T3-chat-renderer-class921-7d62`; permanent report [here](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_RENDERER_CLASS_SH48_2026-11-05.md).