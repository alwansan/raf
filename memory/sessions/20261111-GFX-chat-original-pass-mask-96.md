## 11 Nov 2026 — GFX138 Windows Forward/Deferred exact-mask CI VERIFIED

Session `20261111-GFX-chat-original-pass-mask-96` (`origin=chat`). [Windows Actions 43064118522](https://github.com/alwansan/raf/actions/runs/43064118522) completed **SUCCESS** at `9653fb464cab03b6bcc688bbbb3926bb758fa066`. The actual job log shows **10/10** synthetic negative/positive tests passed, then both source-original DXBC Forward and Deferred were executed on WARP within the same private stage. **7/7** original Forward+Deferred RT0 coverage masks matched pixel-for-pixel, each with **2,008 covered pixels**, **0 displaced pixels**, and SHA256 `539a7b7685e303394c783b9a9b88deeda9bc775cd3df041263f51e6a4f1b7f91`. GFX136 Deferred original controls simultaneously passed: flat normal changed RT2 in 2,007 pixels and no other target; nonmetal changed RT0/RT1 in 20/2,008 pixels, no others. See [safe artifact 13876035541](https://github.com/alwansan/raf/actions/runs/43064118522/artifacts/13876035541). Private original sources and raw readbacks were purged; artifact contains only GFX136/GFX138 safe aggregates.

**Scope:** controlled Windows DXBC source-original pass coverage and material effects. Windows–Mesa RGB full-image equality is NOT proven, original Unity ShaderLab pass/state selection and actual G-buffer formats remain unverified, and no GFX135/GFX138 private combined signed owner APK or Adreno 9-case batch has been delivered. Batch plan: **9 tests / 51 captures**. Original game PC↔Android scene pixels and full animation playback remain OPEN; `originalShaderRestored=false`, `originalAnimationRestored=false`, `phase_closed=false`.


---

## 11 Nov 2026 — GFX138 original Windows Forward versus Deferred mask gate

Session `20261111-GFX-chat-original-pass-mask-96`, `origin=chat`, writing only to `experiment/android-graphics-rootcause`. Base `239808dbc7390c323f6aa0aac9884b258d0f1ea7`.

GFX136's actual original Windows D3D11 WARP Deferred result recorded 2,008 coverage pixels, and its RT0 mask SHA256 `539a7b7685e303394c783b9a9b88deeda9bc775cd3df041263f51e6a4f1b7f91` exactly equals the prior source-pinned original GFX121 Forward mask SHA256. A matching count alone could hide displaced pixels, so GFX138 adds an independent source-free fail-closed exact per-pixel alpha comparison across four original Windows Forward controls and three Deferred RT0 controls, checks prior safe Forward SHA and Mesa coverage count, rejects bad-length/nonbinary images and shifted coverage with unchanged pixel count. The pinned GFX136 Windows workflow now reruns original DXBC Forward and Deferred using the same stage/source texture preparation in one private job, runs GFX138 unit tests and uploads only aggregate safe JSON. Original assets/readbacks are purged with the existing `if: always()` cleanup. **CI new workflow result is pending**; no phone test or signed owner APK produced. Actual Unity shader/pass selection and native G-buffer formats, original game scene parity, inter-driver RGB differences, original animation playback and final Android acceptance remain open. `phase_closed=false`.


---

