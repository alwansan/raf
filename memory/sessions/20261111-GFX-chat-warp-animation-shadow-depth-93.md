## 11 Nov 2026 — GFX130 Windows animated Forward and GFX131 Mesa ShadowCaster

Session `20261111-GFX-chat-warp-animation-shadow-depth-93`, origin=chat. Write only `experiment/android-graphics-rootcause`.

[Windows GFX130 run 43057213502](https://github.com/alwansan/raf/actions/runs/43057213502) rebuilt the 15 M02 pose vertex buffers from the pinned source and verified every vertex-buffer hash against Mesa before drawing. Original DXBC ran using the fixed union-of-poses camera. All 15 coverage masks matched Mesa exactly; no complete RGBA image matched, and the magnitude of RGB differences remains unmeasured. Windows reproduced the 1/5/5 distinct images per clip. Artifact 13872540965 contains safe aggregate data only. GFX121 base regression run 43057213470 passed.

GFX131 selected the unique M02 depth ShadowCaster candidate after filtering material keywords absent from that pass. Verified offline GLSL link, then drew on Mesa using original Shader48 translated stages, source material, geometry and texture. The source UnityPerDraw buffer contains three WorldToObject rows; the staging tool validates its exact DXBC extent before packing. With controlled zero bias, the source depth mask covered 2,008 pixels and matched the Forward mask. Opaque control also covered 2,008; zero-alpha and depth-write-off controls each covered zero. Six CBs and one combined sampler bound. Integrated Mesa replay retained Forward, ForwardAdd and all 15 animation results. Portable shadow assets and four references prepared locally. They are not yet in the Android runner. No new signed or phone-run APK.

Unity runtime variant and state selection, Windows ShadowCaster and phone depth validation, Deferred, original clip playback and original PC gameplay comparison remain open. `phase_closed=false`.

