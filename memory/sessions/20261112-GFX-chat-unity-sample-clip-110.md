## 12 Nov 2026 — GFX151 reconstructed sample clips run through Unity

Session `20261112-GFX-chat-unity-sample-clip-110`, origin=chat. Write only `experiment/android-graphics-rootcause`.

[Unity run 43104902312](https://github.com/alwansan/raf/actions/runs/43104902312) sampled three reconstructed AnimationClip instances via SampleAnimation on a private M02 hierarchy, using five keyed source-derived poses per clip at normalized times. Native BakeMesh matched all 24,990 positions within the existing tolerance, max absolute error 0.0001220703125. Regression 43104902002 passed. Safe artifact 13894110820.

Source-derived curve continuity audit: 87 and 198 junctions on the two moving clips, maximum endpoint mismatch 3.10e-8; no junction exceeded 1e-5. The constant clip has no streamed junctions. Next reconstruct continuous source curves using Hermite tangents and verify off-key frames through a native Animator/Playable route. Current sampled clips do not preserve continuous interpolation, original serialized clip identity or original AnimatorController execution. Actual shader pass state and matched original PC scene remain open. No phone retest or new APK. `phase_closed=false`.

