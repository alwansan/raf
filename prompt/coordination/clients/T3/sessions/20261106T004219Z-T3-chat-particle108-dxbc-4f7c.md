# T3 chat — original Particle108 one-Pass genuine four D3D11 VS/FS pairs

- identity T3; origin chat; session_id: 20261106T004219Z-T3-chat-particle108-dxbc-4f7c; issue: RENDER-002 OPEN / NOT_READY.
- Registered before edits: prompt/coordination/work/RENDER-002/20261106T004219Z-T3-chat-particle108-dxbc-4f7c.json (commit 0287dd16fce0ef23331597ec959e89e705f5a31a), base HEAD 951a48a9d0f958ad09719058d2f7575d54249390.
- resumed from T3 chat 20261106T001837Z-T3-chat-particle108-shaderlab-5d72 and scheduled 20261106T0030Z-T3-scheduled-native-stage-order-e6b4; separate from T5 native build.
- experiment key: T3-ZIP2-15964ea8-6scenes-4SHAowners-108ParticleShader48-onePass-D3D11-true-linked-VSFS-keyword-pairs-sourceonly-v1.

## Real CI source proof

- https://github.com/alwansan/raf/actions/runs/42139137265 COMPLETED SUCCESS exact source HEAD 927bf1d096f8c5500f237794b91fc71c90a946ab; 117/117 source-free tests PASS (23+13+9+7+7+9+11+5+11+22). Original six scenes and four Shader owners from immutable ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385, SHA-authenticated 269007288 owner bytes. Original one resource stream SHA checked and three private Texture2D byte ranges verified.
- Private authentic six-scene Renderer→Material→Shader graph yields ONE 108-source-particle-slot Shader48, 54 source Particle Renderers, one normal source Pass, RGB ColorMask/Alpha Blend and ZWrite OFF.
- ORIGINAL source platform4 D3D11 has 16 record entries, 4 genuine Vertex stage +4 genuine Fragment stage variants, 4 exactly paired keyword permutations, 8 distinct linked stage programs, 6 keyword-bearing stage records, ZERO unpaired VS/FS variants. This is source bytecode linkage, NOT original-to-Android SPIR-V/ShaderLab or GPU pixel equivalence.
- Prior real [CI42136474867](https://github.com/alwansan/raf/actions/runs/42136474867) showed exact source-selected plain AssetRipper .shader contains //DummyShaderTextExporter despite one fake-looking program block; prior [CI42134436841](https://github.com/alwansan/raf/actions/runs/42134436841) proved 10/10 Material→Texture GUID bindings. Neither result identifies the exact installed phone fire/smoke emitter.

Code: scripts/t3_original_particle108_dxbc_feasibility.py (real source SHA+stage table join), tests/test_t3_original_particle108_dxbc_feasibility.py (nine adversarial cases), isolated .github/workflows/raft-t3-original-renderer-shader-impact.yml (read-only original CI). No original shader program bytes or SHA/IDs/GUIDs/labels exported; no game assets, Android APK/OBB, sound/Settings, input, water, save touched, and no other workflow canceled.

Full report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE108_DXBC_LINKAGE_2026-11-06.md
Resource: https://github.com/alwansan/raf/blob/feature/android-native-port/prompt/coordination/B_TEAM/resources/T3-original-particle108-authentic-D3D11-variants.json
Next: Translate original exact Particle108 four VS/FS D3D11 matched keyword variants to Vulkan SPIR-V in disposable source runner, check per-stage IO/resources/alpha, and verify T5 production post-restorer exact Shader48 GUID and user's device emitter before modifying real game assets.

## Canonical team index and source-vs-device boundary

- Appended run 42139137265, report and immutable DXBC resource record to OPEN `prompt/coordination/B_TEAM/issues/RENDER-002.json` at commit `0a60835eb5fe134c20a2d56ddc54910bc633c8f7`.
- [Canonical team summary refresh run 42139827190](https://github.com/alwansan/raf/actions/runs/42139827190) COMPLETED SUCCESS at source commit `6e6a05976da174039b6df25c458d0dacca96d09e`. The public resource explicitly reports 4 exact original Vertex/Fragment keyword permutations and `device: NOT_TESTED`. It does not assert that T5 production native ShaderLab or Adreno pixels are fixed.
- No source shader bytecode was published, no production game asset or native Android build touched, no other client's CI canceled. Scope can be released.
