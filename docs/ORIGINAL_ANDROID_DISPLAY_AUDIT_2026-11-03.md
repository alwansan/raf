# Original Android display mutation audit — 2026-11-03

**Scope:** read-only structural investigation of the owner's Settings-only aspect/resolution regression. No Unity Editor, native game build, APK/OBB/XAPK, release, device test, original asset change, or scheduled automation modification. Only `feature/android-native-port` is writable.

## Verified implementation and CI

- Source/test/workflow commit: [315639e7cfac17685bd961038cd81d1f177bbef4](https://github.com/alwansan/raf/commit/315639e7cfac17685bd961038cd81d1f177bbef4).
- [Original-source offline integration 41536225034](https://github.com/alwansan/raf/actions/runs/41536225034) **COMPLETED SUCCESS** on the exact commit: synthetic lexer/readonly tests, private ILSpy CSharp9 decompilation, original adapter/harness checks, and managed C# compile passed.
- New `scripts/probe_original_android_display_paths.py` scans decompiled C# privately, masking comments/literals; reports only source basenames, hashes, line numbers, and direct display-mutation categories. It neither publishes original code nor changes the game. Four synthetic tests passed locally and in CI.

## Authentic source evidence

The probe inspected **2,394** original C# files. It found **three** direct display mutation sites in its *bounded categories*:

- `GraphicsSettingsBox.cs` SHA256 `e1854d74adbbe0565b586ec749f7de2cc73e3f97f59c388934a3faa0defc9300`: one `Screen.SetResolution` call at original source line 565. The existing Android-specific adapter inserts an early return in `ApplyCurrentResolutionAndFullscreenMode`; this is source-level protection only.
- `DynamicResolution.cs` SHA256 `69f9ab873de44b167deb3d6d00182fd59b0147b27d8365fff64b2849069cedbc`: two `ScalableBufferManager.ResizeBuffers` calls at original source lines 37 and 55. Their runtime invocation conditions and horizontal/vertical scale arguments are **not yet established**.
- The scan found no direct `Screen.orientation` or `Screen.fullScreenMode` assignments in the decompiled C# within its explicit patterns. It does **not** cover native/Unity engine internals, indirect calls, CanvasScaler/RectTransform changes, preprocessor reachability or third-party code outside this assembly.

## Interpretation and next discriminating test

**Confirmed:** there is a second original display mutation owner beyond `GraphicsSettingsBox`, so treating the Settings guard as an exhaustive resolution fix would be incorrect. **Not confirmed:** whether `DynamicResolution` changes aspect ratio, is invoked by Settings, or causes the owner's observed regression.

Next inspect the original `DynamicResolution` call arguments, lifecycle and references from the Settings path in private source-only CI, preserving source SHA and only structural output. Determine whether width/height scale factors differ or another UI layout path is responsible. Only then implement a narrow Android guard if the evidence warrants it. The owner's existing phone logs are from APK80 and cannot validate source-only changes. Full Unity/APK build remains explicitly on hold.
