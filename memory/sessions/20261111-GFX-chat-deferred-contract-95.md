### GFX137 VERIFIED CI addendum — 11 Nov 2026
[GitHub Actions 43062691619](https://github.com/alwansan/raf/actions/runs/43062691619) COMPLETED SUCCESS at commit `91fce78d05da873e8cd2a596b77f1d773b48813f`. Inspected actual job log: all 13 source-free tests passed, including full GFX124 ZIP integration and forged-yet-self-consistent readback counter/hash rejection. No private source assets built/published. This verifies the new audit software, **not** an Adreno Deferred render or original Unity gameplay/G-buffer semantics. `phase_closed=false`.

---

## 11 Nov 2026 — GFX137 source-free Android Deferred acceptance hardening

Session `20261111-GFX-chat-deferred-contract-95`, origin=chat. Write only `experiment/android-graphics-rootcause`. Base was GFX136 commit `12abc3bdc2a318cd710fb8ccb36267a4cdfbe13b`.

Verified GitHub Actions GFX135 shell 43060277689 and original Windows DXBC Deferred GFX136 run 43060483182 both completed SUCCESS. GFX136 covered 2,008 pixels with original DXBC four-target Deferred readback; flat normal changed 2,007 pixels in RT2 and no others; nonmetal changed 20/2,008 in RT0/RT1 only. Mesa coverage previously matched. This is a controlled four-RGBA8 target fixture, NOT verified original Unity G-buffer or phone pixels.

GFX137 introduces independently checked 12 Deferred capture contract: reference/device RT0 alpha masks must match exactly and remain invariant across controls; unchanged MRTs must remain byte-identical; normal and metallic controls must affect their expected targets; all twelve readbacks must be present and correct length. The audit adds covered RGB mean absolute channel error and max channel error for each target against the signed APK's Mesa reference, without assuming exact inter-driver RGB equality. Synthetic source-free positive/negative tests include full GFX124 ZIP auditor integration with recomputed valid hashes, demonstrating that control tampering is rejected. Local isolated Python controls 12/12 PASS; integration and GitHub Actions result must be checked independently.

The one-APK batch now plans **9 cases / 51 readbacks** (four Forward material slots, one combined, one ForwardAdd, 15 animation, 4 ShadowCaster, 12 Deferred captures). The public Actions GFX135/GFX124 build remains source-free; it is NOT a distributable signed APK with original assets and has NOT been run on Adreno. No private source material or readback was published. Remaining original runtime ShaderLab pass/state selection, genuine Unity G-buffer format, Windows-Mesa numeric RGB parity, single owner APK on phone and source PC gameplay parity. `originalShaderRestored=false`; `originalAnimationRestored=false`; `phase_closed=false`.

