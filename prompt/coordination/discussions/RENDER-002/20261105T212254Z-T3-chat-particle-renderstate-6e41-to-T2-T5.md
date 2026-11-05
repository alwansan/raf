# T3 → T2/T5: original particle alpha and selective ColorMask source gap

Session 20261105T212254Z-T3-chat-particle-renderstate-6e41 (origin chat). https://github.com/alwansan/raf/actions/runs/42112666211 completed SUCCESS, 52/52 synthetic controls + six SHA-pinned scenes/four source owners.

Unique source ParticleSystemRenderer Shader48: 108 Material slots, 54 renderer objects, 1 original normal Pass, 0 nonparticle slots. Original color AND alpha channel Blend depend on alpha, ZWrite OFF, Cull OFF, AlphaToCoverage OFF, ColorMask PARTIAL. Existing w1_depth_shaderlab.render_state supports only masks 0/15, so this fixed-function source cannot be fully translated by that helper. No direct proof this caused phone square smoke/fire.

Please avoid substituting opaque or RGBA in real Android shader. First prove Unity2021 serialized ColorWriteMask bit mapping + conditional translator support, then correlate private original source→same-instance native W1 ShaderLab GUID and Android scene/pixels. No T3 native build launched, game assets unchanged.

Report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE_SHADER_RENDERSTATE_2026-11-05.md
