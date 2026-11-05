# T3 — authenticated original 108-use Particle Shader48 fixed-function state

**RENDER-002: OPEN / NOT_READY. Original source-only diagnostic, no device-rendering claim.**

## Verified source and CI

- [GitHub Actions 42112666211](https://github.com/alwansan/raf/actions/runs/42112666211): completed SUCCESS, exactly SHA df6c913c249c09d4aa7cf58dee6723160e99ddba.
- Source-free test suites: 21 original Renderer, 9 new Particle render-state, 22 B03 = **52/52 PASS**.
- SHA-verified six original Raft scenes and four Shader/Material owners, immutable ZIP2 provider commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385. 269,007,288 owner bytes reassembled without LFS.
- Unique source Shader48 covers 108 original ParticleSystemRenderer Material slots, 54 distinct ParticleSystemRenderer objects and 0 nonparticle slots in the six original scenes. It contains one normal original Shader Pass. Source Shader identity was selected privately through authentic Renderer → Material → Shader48 links, not guessed from names.

## Original single-Pass Render State (source only)

| Serialized original state category | Evidence |
|---|---|
| Color blending | **ALPHA_DEPENDENT** |
| Alpha-channel blending | **ALPHA_DEPENDENT** |
| ZWrite | OFF |
| Cull | OFF |
| AlphaToCoverage | OFF |
| ColorMask | **PARTIAL**, neither 0 nor full RGBA |
| Depth test | enabled numeric |
| rtSeparateBlend | false |
| Existing w1_depth_shaderlab.render_state translator supports complete state | **false** |

The existing translator intentionally supports only ColorMask 0 or 15, so this authentic partial mask is a guaranteed unsupported input to that translator; other unsupported fields may also exist. Unity 2021.3 documents ColorWriteMask flags and ShaderLab channel subsets; precise mapping from the serialized bitfield needs independent proof before reconstructing the original state. Never replace it blindly with RGBA or opaque blending.

These values do **not** prove the observed square fire/smoke pixels use this shader, that fragment alpha/discard is correct, that its original texture/keywords are linked to the full-native export GUID, or that Android graphics now render correctly.

## Changes, safety, next

- Private in-memory source count handoff: https://github.com/alwansan/raf/commit/79fc823532812d44f6e4d8c4881d9bba284ad043
- Outparam privacy tests: https://github.com/alwansan/raf/commit/7fad4441c29bc7112bb6d7fdc260a81df9ce657b
- New read-only source state classifier: https://github.com/alwansan/raf/commit/9207acc55dfb988a8826ed0725c3fb9032655089
- Nine new source-free tests: https://github.com/alwansan/raf/commit/6b9a7c8ffcad33158274013a7552759658a11035
- Bounded authentic original CI integration: https://github.com/alwansan/raf/commit/df6c913c249c09d4aa7cf58dee6723160e99ddba

Only SHA-verified original inputs were read. No original game file, Unity Shader, .meta/GUID, native build job, APK/OBB, save, Settings, audio or input was changed. No private source names/IDs/GUIDs, HLSL or raw Render State were published.

**Next:** authenticate selective ColorMask bit/channel mapping for Unity 2021.3, guard the translator with regression tests before any actual change, and use exact private source→same-instance full-native export GUID + device screenshot to establish whether this Shader causes square particle effects. Keep RENDER-002 OPEN.
