# 20261110-GFX-chat-shader-binary-variant-links-10
- session_id: 20261110-GFX-chat-shader-binary-variant-links-10; origin: chat
- resumed_from: 20261110-GFX-chat-compiled-platform-probe-09
- base_sha: 14c66bc628da467be4c7b3803c12afe6c882db16
- experiment_key: GFX-MULTI-010-private-pass-to-binary-variant-links
- scope: one source-only audit of exact original Shader48 per-pass m_BlobIndex and m_GpuProgramType vs private decompressed Unity program table; no original game/APK build; no source code or model images exported.
- runs: GFX-MULTI-009 42728348900 COMPLETED SUCCESS, 59 tests; new GFX-MULTI-010 workflow push pending.
- prior counts: 1656 parsed compiled ShaderProgram entries, source platform field D3D11; 188 entries GPU type labelled GLES families, no raw-content magic match, 163501 compressed blob bytes vs 242218471 reported code bytes; investigate consistency before calling any program executable.
- negative controls: out-of-range blob index detected, bad program type mismatch detected, zero original shader restoral claims, no proprietary assets in Git.
- outcome: GFX-MULTI-010 source-only CI requested; phase OPEN.
