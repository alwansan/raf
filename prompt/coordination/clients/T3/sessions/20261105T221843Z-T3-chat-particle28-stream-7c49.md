# T3 chat — source 108 ParticleShader48 actual Texture2D28 and streamed provider dependency

- session_id: `20261105T221843Z-T3-chat-particle28-stream-7c49`; origin: **chat**; identity: **T3**; issue: `RENDER-002 OPEN / NOT_READY`; work status: completed.
- resumed_from: `20261105T2204Z-T3-chat-particle108-mattex-a4c6` (source Material TexEnv) and `20261105T213100Z-T3-scheduled-clstage-8b4f` (independent LogRaft screenshot timing).
- base_sha: `04b24a431be8e24204e6ad4bc1471c2460863792`; work registered before edits in `prompt/coordination/work/RENDER-002/20261105T221843Z-T3-chat-particle28-stream-7c49.json`, commit `ec9d5539a81be13be8e1a1fb0fd42618333f8119`.
- experiment_key: `T3-zip2-SHA15964-sixscene-4owner-particle108-5material-3target-local-Tex2D28-manifeststream-typed-v1`.
- resource_key: `t3-ZIP2-sixscene-four-owner-only-22min` released at terminal run.
- modified: `scripts/t3_original_particle_material_texenv.py` (`222654d6ae04d63678c3663bd43c0e081ab7afeb`), new `scripts/t3_original_particle_texture_targets.py` (`9cf384847fd4bd4e1fc8d1c8ebd67a0afbf788b2`), new `tests/test_t3_original_particle_texture_targets.py` (`d7825fd6e80adfa8ea3db48299ddd3b054050d91`), `.github/workflows/raft-t3-original-renderer-shader-impact.yml` (`87ca7a76309ef68e69dcb65b1dff9c822482694c`), this session/work/experiment/event/report and T5 discussion. Attempted a redundant private-output test edit in existing MatTex tests but GitHub action was disallowed; no change from that attempt, seven new source-free tests in independent file passed.

## Authenticated real proof

[CI 42120918486](https://github.com/alwansan/raf/actions/runs/42120918486) on exact source `87ca7a76309ef68e69dcb65b1dff9c822482694c`: **SUCCESS**, 23 original Renderer +13 source original Particle State +7 source Material +7 new Texture2D28 +5 W1 Depth +11 B25 Foam +22 B03 = **88/88 tests PASS**. SHA verified six original Raft scenes and four original Material/Shader owners from immutable ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` (269007288 assembled original owner bytes). No native exporter or Unity build launched.

Real original source top ParticleShader48: 108 Renderer Material slots, 54 Renderer objects, 5 distinct Material21, 10 bound nonnull local TexEnv PPtrs, three distinct local texture targets. **All three** PPtr targets resolve to true **Texture2D class28** original serialized objects, with valid positive dimensions/format/image-size metadata. **All three** have nonempty original `m_StreamData` with extents within immutable ZIP2 manifest length, from **ONE original external .resS/.resource provider**. In this minimal sixscene/four-owner source-only run, the provider's external payload is **not staged** (3/3 dependencies), and actual source .resS SHA/pixels were not verified. The native build may independently stage/include it: no Android missing-resource conclusion.

Previous [CI 42116530618](https://github.com/alwansan/raf/actions/runs/42116530618) established original ParticleShader48 ColorMask RGB, alpha-dependent Blend, ZWrite OFF and default strict fixed-function converter opt-in success; this run does not prove emitted effect or phone rendering.

**Explicit proof boundary:** actual exported W1 Material/Shader GUID and B02 Texture2D28 trace, staged full external .resS payload hash and ImageData decode, GPU format/sampler/alpha, real installed device emitter and square-fire screenshot remain unknown. No game asset, texture bytes, .meta, Unity shader, APK/OBB, water, input, Settings, sound, save or other client's workflow was changed/cancelled.

## Handoff

Permanent report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE108_TEXTURE2D_STREAM_2026-11-06.md

Next: T5 joint bounded/real full-native: use same-instance private original W1 Material21 and B02 Texture2D28 export trace to match 5 authenticated original Materials / 3 original Texture2D class28 to exported Unity GUIDs, actual TexEnv source parity and real full pipeline .resS provider bytes; correlate installed signed APK/OBB emitter and alpha/render pixels. Do not launch equivalent heavy export from T3 uncoordinated; source-only checker can be reused.

## Canonical evidence refresh

[GitHub Actions 42121705420](https://github.com/alwansan/raf/actions/runs/42121705420) **SUCCESS** on workflow change `6361e9cc3e97e129f5de67ef6e94f77d94b64252`. Regenerated T-team canonical evidence index with real SHA-original 3 Texture2D28 stream dependencies; issue RENDER-002 remains OPEN, no Android pixel or game acceptance.
