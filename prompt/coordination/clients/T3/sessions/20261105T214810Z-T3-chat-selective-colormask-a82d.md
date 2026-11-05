# T3 chat — Unity2021 selective ColorWriteMask original Particle source translation

- **session_id:** `20261105T214810Z-T3-chat-selective-colormask-a82d`; **origin:** chat; **identity:** T3; **issue:** RENDER-002 OPEN; **status:** completed (source-only translator with opt-in).
- **resumed_from:** `20261105T212254Z-T3-chat-particle-renderstate-6e41` (chat); `20261105T213100Z-T3-scheduled-clstage-8b4f` (CL logger source timing).
- **base_sha:** `19a8e9fc02c3cd22c6f09857779f5199f9eb3a12`; reserved scope before edits in `prompt/coordination/work/RENDER-002/20261105T214810Z-T3-chat-selective-colormask-a82d.json`, registration commit `9d492312dd3028156c32ae6be3f3cc71a5091571`.
- **experiment_key:** `T3-unitycsref-2021.3-GraphicsEnums-855eebe-ColorWriteMask-ABGRbits-to-ShaderLabRGBA-partialmask-original108-source-v1`.
- **resource_key:** `t3-zip2-6scene-4owner-authentic-shader-state-22min` — released after terminal CI.
- **scope:** `scripts/w1_depth_shaderlab.py`, `scripts/t3_original_particle_shader_state.py`, `tests/test_t3_original_particle_shader_state.py`, `.github/workflows/raft-t3-original-renderer-shader-impact.yml` plus session/work/experiment/event/doc/discussion. The registered legacy W1/B25 test files were intentionally **not modified**; their default behavior remains fail-closed and their existing tests pass.

## Source-verified result and behavior distinction

- Unity 2021.3 actual GraphicsEnums.cs `ColorWriteMask`: A=1 B=2 G=4 R=8, All=15, checked GitHub UnityCsReference **2021.3** branch blob `855eebe69c60dcaea85a74d91656fc02df43ea90`. Official 2021.3 ShaderLab `ColorMask` accepts combinations such as `RGB`.
- Original ZIP2 six scene and four original owner SHA verified; original ParticleShader48 private source target unique 108 slots / 54 ParticleRenderer objects, one Pass.
- Actual original fixed function **ColorMask RGB (mask=14)**; Color+Alpha Blend ALPHA_DEPENDENT, ZWrite OFF, Cull OFF. Legacy default original state translator returns `accepted=false`; isolated explicitly opt-in `allow_selective_color_mask=True` returns `accepted=true`.
- New implementation commit `8a8b0563419ed7292b494b50dc5726bc0ebf37ce` adds ABGR-bit subset helper; follow-up `92b8c5111174cddace33c0944318c1a66f77ba5d` preserves legacy W1/B25 default. New source-only classifier commit `f59da45f7031f0495cea791237f0bfe80bff60b3`, 16-mask+privacy synthetic controls `22b06730fa2ca7893e448c2596fb6c4004c82e35`; bounded existing source CI update `d6926a0bbd862cf3a8af0fd6ee0b5da018bdaf2d`.
- [CI 42116530618](https://github.com/alwansan/raf/actions/runs/42116530618) **COMPLETED SUCCESS** on exact workflow SHA `d6926a0bbd862cf3a8af0fd6ee0b5da018bdaf2d`. Python compile + **21+13+5+11+22=72/72 tests PASS**, authentic original six scenes/four owner SHA verified, 269007288 original owner bytes.

## Limitations, no collisions

This is a **source-only fixed-function ShaderLab string translator**, not a restored or compiled executable shader. No raw shader names, GUIDs, IDs/HLSL/source or original asset bytes uploaded. No game Shader/.meta, asset binding, water/FFT, audio, Settings, save, controller or native Android build was modified. W1/B25 legacy default still explicitly rejects partial ColorMask and their tests pass. Other clients' jobs were not cancelled.

Original exact 108-source shader→same-instance native W1 export GUID and device screenshot emitter/pixel association remain unknown. `RENDER-002` stays OPEN and READY is not implied. Permanent report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE_COLORMASK_MAPPING_2026-11-06.md.

**Next:** Use the original 108-use particle Shader48 private ID, same-instance native W1 export GUID, and installed Android package scene/prefab/material trace to compare source ColorMask RGB and Blend to actual compiled ShaderLab and failing pixels. Only then consider editing a game shader. Do not duplicate source-only ZIP2 runs or declare RENDER-002 ready.
