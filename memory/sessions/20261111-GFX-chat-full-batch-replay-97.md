## 11 Nov 2026 — GFX139 & GFX140 complete source-free 9-case APK packaging acceptance

Session `20261111-GFX-chat-full-batch-replay-97`, `origin=chat`, writing only `experiment/android-graphics-rootcause`.

**GFX139 [CI43068059010](https://github.com/alwansan/raf/actions/runs/43068059010) SUCCESS:** reviewed actual 7/7 passing Python integration tests. The production GFX124 private ZIP packer constructed a **9-case / 51-capture** package from synthetic fixtures (39 PNG + 12 raw RGBA); the production owner ZIP auditor accepted complete replay, accepted explicit 8/9 partial-failure reporting, and rejected forged Deferred changes with recomputed counters/hashes, missing PNGs, changed case order, reference hash drift and extra fixture entries. The synthetic ZIP shell is NOT an installable APK.

**GFX140 [CI43069997709](https://github.com/alwansan/raf/actions/runs/43069997709) SUCCESS:** compiled the actual Android GFX124 MainActivity and binary Manifest via Android SDK, injected synthetic 9-case fixture into **the real compiled shell**, ZIP-aligned and APK-signed using a disposable test key, verified **v3** signature with minSdk 29, checked 235/235 fixture asset payloads byte-for-byte before/after signing, then replayed all **9 cases / 51 captures** through the production auditor **against the signed APK**. The actual CI JSON reports `apk_signature_v2_verified=false`, `apk_signature_v3_verified=true`; do **not** misreport v2. CI initially failed when accidentally injecting into GFX139's text fake Manifest; fixed to use Android binary Manifest. A second false-failure gate incorrectly demanded that the default APK verifier explicitly report simultaneous v2 and v3 success; minSdk29 can use verified v3. The final signing+audit run succeeded. Safe artifact [13878690193](https://github.com/alwansan/raf/actions/runs/43069997709/artifacts/13878690193) contains aggregate JSON only; no APK, original mesh/shader/texture or device logs were published.

**Not yet done:** reconstruct owner-private original Shader48 / model / mips for the final APK, assemble and sign that private real-assets APK, run Adreno 730 9-case/51-readback export and audit, validate original Unity pass states and G-buffer formats, actual Animator clip playback, PC–Adreno matched scene RGB/depth/alpha/shadow pixels. `originalShaderRestored=false`, `originalAnimationRestored=false`, `phase_closed=false`. No T1–T5/main/zip2 branch modifications.

---

## 11 Nov 2026 — GFX139 / GFX140 synthetic batch integration

Session `20261111-GFX-chat-full-batch-replay-97`, origin=chat, only write `experiment/android-graphics-rootcause`.

Verified [GFX139 CI 43068059010](https://github.com/alwansan/raf/actions/runs/43068059010) completed **SUCCESS** on commit `4e06f8f9e04e26f614f1050ab59c129b7e9f4a5e`. Reviewed actual job log: 7/7 source-free tests PASS, including production GFX124 pack→synthetic 9-case, 51-readback zip→owner ZIP audit (39 PNG + 12 raw RGBA), partial failure 8/9, and five negative payload/metadata mutations. This authenticates the ZIP packer and auditor integration, **not** original source or device GPU pixels.

Added GFX140 source-free signed Android APK smoke: compile production GFX124 Java and manifest, inject synthetic 9-case fixture, zipalign, ephemeral test-key v2/v3 sign, compare every packaged asset hash and rerun production ZIP audit against the signed APK; CI workflow uploads only safe metadata, never a private APK. GFX140 CI still pending at initial commit. No original asset or raw shader/data published. `phase_closed=false`.

