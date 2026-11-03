# A2 — Authenticated Settings layout source inventory (3 November 2026)

Client: `raft-20261103T095700Z-a2b31f4d`. Original source-only test commit: [b4ab727](https://github.com/alwansan/raf/commit/b4ab7275cdadead58081d188cea305d8aa814766). [GitHub Actions 41616959190](https://github.com/alwansan/raf/actions/runs/41616959190), job125852692510: **COMPLETED SUCCESS**. Four synthetic unit tests passed; the real original CSharp9 private-source scan passed all three SHA256 pins.

Authenticated original input: 2,394 C# files, eight Settings-related classes in scope, 20 bounded lexical UI geometry/screen signals. `GraphicsSettingsBox.cs`:12 Screen resolution reads, one known `Screen.SetResolution` line565. `DynamicResolution.cs`: two `ScalableBufferManager.ResizeBuffers` lines37,55. `Settings.cs`:three `RectTransform` type references lines41,44,47. `ControlsSettingsBox.cs`: `RectTransform` reference line51; one `sizeDelta` assignment line110.

No direct CanvasScaler, referenceResolution, matchWidthOrHeight, screenMatchMode, screen width/height, anchor/localScale, camera aspect setter found **within these eight source classes**. These lexical findings are **not** a runtime call graph, a proof of Settings aspect regression, or a review of serialized scene UI components; other classes, aliases, reflection or Unity engine layout may matter. The original Android guard for desktop `Screen.SetResolution` and DynamicResolution sample-validation fix are unchanged. **DISPLAY-003 remains SOURCE_REVIEW_REQUIRED.**

The scanner prints source basenames, hash, counts and line numbers only. Original C# bodies and original assets remain private. No Unity, new APK/OBB/XAPK, Release, new native request, LFS, gameplay code, shaders, .meta/GUID, touch or automation changes occurred. WATER-001/RENDER-002 remain open and game remains **NOT_READY / 0 of 3 candidate reviews**. Next source-locked experiment: inspect the `ControlsSettingsBox` line110 assignment target and original serialized Settings CanvasScaler/RectTransform component data before any runtime fix.


<!-- A2-DISPLAY-003-CONTROLS-CI41623586923 -->
## Follow-up: pinned executable Controls sizeDelta context — 3 November 2026

[CPU-only original-source CI41623131096](https://github.com/alwansan/raf/actions/runs/41623131096) at [ee8b11e](https://github.com/alwansan/raf/commit/ee8b11e88aee10530f16b927e09d4f37af5694d4) and [refined CI41623586923](https://github.com/alwansan/raf/actions/runs/41623586923) at [b9ec97d](https://github.com/alwansan/raf/commit/b9ec97d2776e8504a0c5d71f1b226e29f320707c) both COMPLETED SUCCESS (refined nine synthetic tests plus original CSharp9 source SHA pin).

Original ControlsSettingsBox SHA256 b64ba19e2d55fe503045e523c3c8658adb4ca3ededaccfecf6521bad1600ef92. Its unique executable `.sizeDelta` write at line110 belongs to method106–112. Receiver matches a `RectTransform` declaration elsewhere in same owner class (not a method RectTransform/Transform parameter); RHS is a simple identifier, not a Vector2 parameter or direct screen-width/height reference. This method has no direct Screen.SetResolution/CanvasScaler scale-property writes or explicit same-owner invocation, and is not a recognized lifecycle method. Lexical context is not causal/serialized scene proof.

DISPLAY-003 SOURCE_REVIEW_REQUIRED, NOT_READY/0 of3; no runtime, Unity/APK/OBB/XAPK, GUID/.meta, LFS, touch, tasks, native requests or release changed. Next inspect authenticated serialized Settings UI CanvasScaler and opening/UnityEvent path.


<!-- A2-DISPLAY-003-SCENE-CANVAS-CI41629641835 -->
## Original non-LFS scene and Unity CanvasScaler PPtr evidence — 3 November 2026

[Final A2 CI41629641835](https://github.com/alwansan/raf/actions/runs/41629641835) SUCCESS at [db9ba867](https://github.com/alwansan/raf/commit/db9ba867619a67bbb05f047fcf17fddd632dfbb2): 11+7 synthetic tests plus six original Git-pinned non-LFS scene blobs and original global MonoScript blob. Original level0: 4 native Canvases/1,644 RectTransforms, 2 Settings-named objects; level1:56 native Canvases/3,033 RectTransforms, 1 Settings-named object. Global owner 3,827 MonoScripts; authentic UnityEngine.UI.CanvasScaler script resolves to 4 scene0 and 13 scene1 MonoBehaviours, all attached directly to a native Canvas GameObject. Exactly one Settings class-*name* MonoBehaviour in each scene is attached to a Settings-named GameObject, but **neither script-bearing GameObject has a verified scaler ancestor in its in-scene native Transform chain**; no inference of absent UI scaling or aspect root cause. Custom CanvasScaler fields still UNDECODED, previous base MonoBehaviour fields are not custom TypeTree. [Detailed original scene report](A2_ORIGINAL_SCENE_UI_CANVAS_2026-11-03.md). DISPLAY-003 SOURCE_REVIEW_REQUIRED; NOT_READY/0 of3. No Unity/APK/LFS/asset or task change by A2.
