# T3 chat — source Particle one-Pass Alpha Blend / ColorMask gap

- session_id: 20261105T212254Z-T3-chat-particle-renderstate-6e41
- origin: chat, identity: T3; issue: RENDER-002 OPEN / NOT_READY; status: completed source-only
- base_sha: 72a49f1452b594e0af3deefeba08085e15c6695a
- work recorded before edit: prompt/coordination/work/RENDER-002/20261105T212254Z-T3-chat-particle-renderstate-6e41.json, commit 249df8cbff1ba67d7351527037f206835e98f2b1
- resumed_from: 20261105T211313Z-T3-chat-particle-shader-rank-4e92
- experiment_key: T3-ZIP2-15964-sixscene-4owner-source108-particle-Shader48-pass0-blend-alpha-zwrite-sourceonly-v1
- resource_key: t3-ZIP2-original-6scene-4owner-source-only-22min (released after completed CI)
- intended_files: scripts/t3_original_renderer_shader_impact.py, tests/test_t3_original_renderer_shader_impact.py, scripts/t3_original_particle_shader_state.py, tests/test_t3_original_particle_shader_state.py, .github/workflows/raft-t3-original-renderer-shader-impact.yml and this session/work/experiment/event/report/discussion

## Actual verified proof

[CI 42112666211](https://github.com/alwansan/raf/actions/runs/42112666211) SUCCESS at df6c913c249c09d4aa7cf58dee6723160e99ddba. Synthetic suites 21+9+22=52 PASS. The exact six scenes + four source owners were SHA authenticated from pinned immutable ZIP2, 269007288 original owner bytes; source original ParticleSystemRenderer top Shader48 108 slots, 54 unique renderer objects, one original normal Pass, zero nonparticle slots. Original m_State: color and alpha blending both ALPHA_DEPENDENT, ZWrite OFF, Cull OFF, AlphaToCoverage OFF, ColorMask PARTIAL, depth test enabled, separate per-RT blend false, existing render_state translator rejected. Source shader names, object IDs and GUIDs remained private.

Existing w1_depth_shaderlab.render_state only accepts color masks 0 and 15. This partial original mask is a confirmed unsupported input, but further unsupported state may exist. This result is original fixed-function ONLY, not authored ShaderLab/HLSL, source → full native exporter GUID, emitted particle, Unity/Android pixels or device cause. Do not change game asset or claim color repair.

## Handoff

Permanent report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE_SHADER_RENDERSTATE_2026-11-05.md. Source code commit 9207acc55dfb988a8826ed0725c3fb9032655089; CI integration df6c913c249c09d4aa7cf58dee6723160e99ddba. T1/T2/T4/T5 jobs were not cancelled. Sound/Settings/world/save/input unaffected. Follow-up: prove Unity serialized ColorWriteMask → ShaderLab mask bit semantics, support selective masks under targeted safety gate, inspect source textures and fragment alpha then match private native W1 GUID and Android screenshots. Work status completed; no lingering CI or resource lock. Do not overwrite T3 scheduled session/state/MEMORY.
