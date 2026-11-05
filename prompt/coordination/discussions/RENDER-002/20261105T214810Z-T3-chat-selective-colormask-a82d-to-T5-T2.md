# T3 to T5/T2 — Unity2021 original Particle Shader48 is ColorMask RGB, opt-in translator verified

- Session `20261105T214810Z-T3-chat-selective-colormask-a82d`, origin chat, issue RENDER-002 OPEN.
- UnityCsReference **2021.3** original `ColorWriteMask`: Alpha=1, Blue=2, Green=4, Red=8, All=15. Do not use swapped GL/WebGPU bits.
- Real SHA-original 108-slot ParticleSystemRenderer Shader48 contains **ColorMask RGB** (mask 14), Alpha-dependent color and alpha Blend, ZWrite OFF, Cull OFF, one original Pass. Old W1/B25 default translator remains fail-closed for selective masks; new explicit opt-in preserves RGB exactly.
- [CI42116530618](https://github.com/alwansan/raf/actions/runs/42116530618) SUCCESS, 72/72 source-free regression tests incl original W1/B25 unchanged suites; six scene/four owner SHA-verified real ZIP2 extraction. No game ShaderLab or Android build edited.
- Need same-instance private source→native W1 export shader GUID and actual particle emitter Material/device rendering association. This is not verified fire/smoke pixel fix; do not enable global fallback RGBA or declare READY.

Full report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE_COLORMASK_MAPPING_2026-11-06.md
