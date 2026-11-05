# T3 → T5/T2: exact original 108-use ParticleShader48 needs ONE streamed source resource provider

Session `20261105T221843Z-T3-chat-particle28-stream-7c49` (origin chat). [CI42120918486](https://github.com/alwansan/raf/actions/runs/42120918486) SUCCESS, 88/88 tests and original sixscene/four-owner SHA.

Source binding now proven: **108 original Particle Renderer Material slots → five Material21 → ten bound local m_TexEnvs pointers → THREE distinct genuine Texture2D class28 original objects**. All **3/3** Texture2D have original nonempty `m_StreamData` within pinned ZIP2 manifest limits, all **ONE external .resS/.resource provider**. The narrow four-owner source-only CI did not stage this provider (0/3 actual payload SHA verified), so source pixels unavailable in that experiment.

**This does NOT prove the signed APK/OBB, full native exporter or device lacks the provider.** The gap for full native is one specific private provider dependency; compare same-instance B02 Texture2D28 + W1 Material21 exported GUID and FULL resource staging (do not print private original IDs, names, resource paths). Validate actual image bytes and installed emitter texture/Shader/Material and phone pixels before changing shader assets. No heavy export/Unity ran, no game modifications, preserve water T1 and audio/Settings.

Permanent report: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_PARTICLE108_TEXTURE2D_STREAM_2026-11-06.md
