## 11 Nov 2026 — GFX132 Android shadow batch, GFX133 Windows depth, GFX134 Mesa Deferred

Session `20261111-GFX-chat-shadow-batch-warp-deferred-94`, origin=chat. Write only `experiment/android-graphics-rootcause`.

GFX132 added native, opaque, zero-alpha and depth-write-off ShadowCaster controls to the Android batch, which now plans eight cases and 39 captures. Empty expected depth captures encode transparent black for lossless PNG round trips. Audit replay of all 39 captures accepts correct empty coverage and detects injected nonzero transparent coverage. Legacy GFX120 audit passed. Local assembly checked 208 private fixture entries against an older shell as a ZIP harness. [Android run 43058814513](https://github.com/alwansan/raf/actions/runs/43058814513) built the source-free shell, artifact 13872821704. No new signed APK or Adreno run.

GFX133 [Windows 43059086364](https://github.com/alwansan/raf/actions/runs/43059086364) executed the original ShadowCaster DXBC candidate and read the D24 depth texture. Native and opaque each covered 2,008 pixels, transparent and depth-write-off covered zero. All four masks match Mesa byte-for-byte. Artifact 13873895040 aggregate only. Base Windows regression 43059085885 passed. Unity variant and fixed-function runtime selection remain unverified.

GFX134 staged the exact original first-subshader M02 Deferred pair and verified offline link and actual Mesa MRT draw in a controlled four-RGBA8 fixture. Coverage equals Forward at 2,008 pixels. Flat normals affect 2,004 pixels only in target 2. Nonmetal affects 20 pixels in target 0 and 2,008 in target 1, with no normal changes. Restoring source inputs reproduced all targets; a fresh prep replay matched the integrated Mesa test. Actual Unity G-buffer format, PC scene pixels, Windows Deferred and Android Deferred are still open. `phase_closed=false`.

