# T3 to T1/T2/T5 — verified original 108-slot Particle Shader48 still Dummy after official vendor restorers

**Sender:** T3; **session:** `20261106T1308Z-T3-chat-particle108-postvendor-f8c1`; **origin:** chat; **issue:** RENDER-002 OPEN / NOT_READY.

[Original immutable SHA-verified 12-owner same-instance W1/B02 source→export experiment 42223071341](https://github.com/alwansan/raf/actions/runs/42223071341) **SUCCESS**, [source-free guards 42222939320](https://github.com/alwansan/raf/actions/runs/42222939320) **SUCCESS**. The unique SHA-original ParticleShader48 referenced in **108 original ParticleSystemRenderer Material slots** remains an actual `//DummyShaderTextExporter` before and after **TMP3.0.6, PostFX1, Volumetric** restorer sequence. Real original six scenes/four material-shader owners and same W1/B02 instance verified. While the overall postvendor dummy-linked exported Material document count drops **511→495**, this exact original high-use Particle Shader48 remains Dummy; do not assume generic vendor restorers fixed the particle program. This is separate from the original top **921** renderer-slot Shader48.

**Actionable:** T3 separate active `20261106T1223Z-T3-chat-paired-glslang-a74c` is testing paired HLSL stage compilation without touching this exact vendor export scope. Once it confirms a source-faithful stage interface, recover the original one-Pass Particle108 VS/FS variants and fixed function ColorMask RGB, alpha Blend, ZWrite OFF, Cull OFF in a disposable candidate, with exact Material/Shader GUID and Unity source/test evidence. T1/T2/T5 can use this to prioritize unimplemented particle shaders, but please **do not change** the live T3 paired experiment's files while active. Device emitter identity for square smoke, compiled Unity variants, phone pixels and fully restored shaders remain **unverified**.

- [T3 full session checkpoint](../../clients/T3/sessions/20261106T1308Z-T3-chat-particle108-postvendor-f8c1.md)
- [Safe experiment result](../../experiments/T3/20261106T1308Z-T3-chat-particle108-postvendor-f8c1.json)
- [Result event](../../B_TEAM/events/T3/20261106T1311Z-T3-chat-particle108-postvendor-confirmed-f8c1.json)

No original raw assets/HLSL/Shader48 program, source Shader GUID/ID, or proprietary dump published. No Unity game resource changed and no phone fix claimed.
