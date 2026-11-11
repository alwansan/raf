## 11 Nov 2026 — GFX139 / GFX140 synthetic batch integration

Session `20261111-GFX-chat-full-batch-replay-97`, origin=chat, only write `experiment/android-graphics-rootcause`.

Verified [GFX139 CI 43068059010](https://github.com/alwansan/raf/actions/runs/43068059010) completed **SUCCESS** on commit `4e06f8f9e04e26f614f1050ab59c129b7e9f4a5e`. Reviewed actual job log: 7/7 source-free tests PASS, including production GFX124 pack→synthetic 9-case, 51-readback zip→owner ZIP audit (39 PNG + 12 raw RGBA), partial failure 8/9, and five negative payload/metadata mutations. This authenticates the ZIP packer and auditor integration, **not** original source or device GPU pixels.

Added GFX140 source-free signed Android APK smoke: compile production GFX124 Java and manifest, inject synthetic 9-case fixture, zipalign, ephemeral test-key v2/v3 sign, compare every packaged asset hash and rerun production ZIP audit against the signed APK; CI workflow uploads only safe metadata, never a private APK. GFX140 CI still pending at initial commit. No original asset or raw shader/data published. `phase_closed=false`.

