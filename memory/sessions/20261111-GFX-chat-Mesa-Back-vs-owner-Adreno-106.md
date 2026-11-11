## 11 Nov 2026 — GFX147.2 VERIFIED: private source-original Mesa Cull images compared against both owner Adreno ZIPs

GFX-LAB session `20261111-GFX-chat-Mesa-Back-vs-owner-Adreno-106` (`origin=chat`), **write only** `experiment/android-graphics-rootcause`; no T-team game branch modifications.

After [GFX147 source-original GPU CI 43093563974](https://github.com/alwansan/raf/actions/runs/43093563974) SUCCESS, with all three source-original M03-1 Mesa Cull Off/Back/Front frame SHA-256 values published as SAFE hashes, I independently **replayed the exact signed original GFX142 APK** using a local EGL GLES3.1 llvmpipe runtime (LLVM **19.1.7**) rather than the CI llvmpipe LLVM **20.1.2**. The locally produced `Off/Back/Front` raw GPU RGBA8 hashes matched the CI values **byte-for-byte in all three cases**: Off `c6d786e908500674d64c3220bf4e26b98253302a88ba390a67b00b570877da78`; Back `3664e3146c10a225dafd9bf490454ea29a94d9e3dbe6d7bb9a4171dfe7ccc4e6`; Front `d28270e7ae29647374d3e5d52fa9eb0d4a1a3e2e55bad2feaf7d6537907bd0b5`. Verified the Off raw bytes are identical to `assets/M03-1/light.rgba` from original signed APK SHA256 `3a4c7fa7f3593325755b32c0f6c5ad941097936b53808666388a4743b5db3773`.

Compared these three exact source-original Mesa frames locally against the **owner's actual M03-1 light Cull Off** capture from each of two GFX124 owner ZIPs (SHA256 `d097f47fcd453eac6d6d82838b3ff2a370ef56794e1823b6311741d297de81d0` and `fad309ffe894acdb4ab5789116330d651c78a5fcec4cef1bacf4516f52288946`); both produce **identical quantitative results**. Validated source APK SHA and original owner PNG/RAW SHA before comparing 3,301 covered source pixels.

| Comparison using SAME recorded Adreno Cull Off image | RGB >10/255 outlier pixels | RGB >30/255 | Max RGB channel | Mean covered RGB absolute error |
|---|---:|---:|---:|---:|
| Adreno Off vs Mesa Off | **58** | 49 | 59 | **0.817530** |
| Adreno Off vs Mesa Back | **135** | 125 | 76 | **1.735030** |
| Adreno Off vs Mesa Front | **2,569** | 2,367 | 173 | **51.215894** |

Mesa Back changes **105** original pixels vs Mesa Off, including **14 of the original 58 Adreno error pixels**; 14 previous hot errors disappear, but **91 new RGB>10 errors appear**, leaving 44 old ones. This is direct numeric counterevidence against merely replacing the Mesa Off reference with Back when evaluating the already-recorded *Adreno Off* image. **This is not the right same-mode test to conclude whether Adreno Cull Back will match Mesa Cull Back**; a new *targeted Adreno Back* GPU image is needed. GFX144's geometric double-faced overlap remains proven; its causal/color remedy is *not* proven. No shader, mesh, material, Unity scenes, Android port game or established 9-case/51-capture baseline was changed.

The private renderer and the owner's ZIP/raw images were used in chat's local sandbox only; raw original game assets, images, keys and private APK have **not** been published to public GitHub. Source-free reproducible comparison code `gfxlab/tools/gfx147_owner_cull_compare.py`, synthetic regressions and CI are published in this session; CI verification is pending on initial commit. The additional [GFX147 private encrypted relay Actions run 43094779535](https://github.com/alwansan/raf/actions/runs/43094779535) completed source Mesa GPU and encryption steps successfully, but its public encrypted artifact upload was still in progress at last inspection; this did **not** block the independent local full-byte GPU replay.

**Next GFX148:** build a *single-target* Adreno original M03-1 Cull Off/Back/Front diagnostic with only 3 cases/readbacks and exact same source Shader48+textures and original Mesa per-mode reference files, share an installable APK safely without exposing game assets; owner performs ONE focused phone test. Continue Unity ShaderLab dynamic Cull/G-buffer format/Animator/runtime original game PC parity separately. `originalShaderRestored=false`, `originalAnimationRestored=false`, `phase_closed=false`.

