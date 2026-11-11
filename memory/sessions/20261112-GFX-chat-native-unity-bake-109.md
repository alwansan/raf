## 12 Nov 2026 — GFX150 native Unity M02 BakeMesh passed

Session `20261112-GFX-chat-native-unity-bake-109`, origin=chat. Write only `experiment/android-graphics-rootcause`.

[Unity 2021.3.45f2 run 43104061232](https://github.com/alwansan/raf/actions/runs/43104061232) successfully reconstructed the source-derived hierarchy poses and called the native SkinnedMeshRenderer.BakeMesh path. Fifteen samples and 24,990 vertex positions, zero vertices outside tolerance 0.0001 + 0.000001 × abs(reference), maximum absolute error 0.0001220703125. Local private inputs verify exact original indices and source positions against signed GFX142 M02 across all samples. GFX113 regression 43104061164 and 18 local GFX108 tests passed. Safe aggregate artifact 13893870288. Only aggregate output, no clip or mesh data published.

This verifies native Unity position deformation for sampled source-derived transforms. It does not establish original serialized AnimationClip or Animator playback, skin normals/tangents, actual Unity shader states or matched PC scene. No new Android APK or phone test required for this result. `phase_closed=false`.

