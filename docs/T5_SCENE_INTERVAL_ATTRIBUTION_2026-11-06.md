# T5 PERF-007 — Preserve loading stalls; prevent cross-scene FPS misattribution

Date: 6 November 2026 (UTC). Writable branch: `feature/android-native-port`. T5 chat session: `20261106T0214Z-T5-chat-scene-window-attribution-8d91`.

## Diagnosed original-phone evidence (not a guess)

Authenticated CL source `520c4cf409aa20a4db54ff80ed87d8807d9cba57` contains actual Unity persistent `performance/sample` and `scene/active_changed` events for the original owner-tested native game.

| Source Unity persistent blob | Last performance sample before active scene switch | Active scene transition | Next performance sample after switch |
|---|---|---|---|
| `413932e92fc24cd50b1fae1cbb25120f392e8158` (20261105T190845373) | 19:10:34.360 UTC, MainMenuScene, 120 frames/23.89 FPS | 19:10:39.991 UTC, MainMenuScene → MainScene | 19:10:41.532 UTC, logged `scene=MainScene`, 96 frames/20.64 FPS, only 1.54 seconds after transition |
| `60674be571e4979e329924e5e2679f43e40ec41a` (20261105T200139667) | 20:04:02.855 UTC, MainMenuScene, 75 frames/14.82 FPS | 20:04:05.078 UTC, MainMenuScene → MainScene | 20:04:08.285 UTC, logged `scene=MainScene`, 12 frames/2.40 FPS, only 3.21 seconds after transition |

Original `AndroidTestDiagnostics.cs` sampled FPS from Unity's `Time.unscaledDeltaTime` and wrote **only** `SceneManager.GetActiveScene().name` at the *end* of a 5-second performance window. Therefore the next record after a transition could contain loading/old-scene frames but be attributed wholly to the new scene. These cross-window intervals cannot establish scene-specific steady-state performance, especially given many additive landmark scene load events in the same time.

This issue is **measurement provenance**, not an established renderer, GPU, or engine frame-time calculation bug. Do not remove scene transition stutters from the metric by resetting/dropping all frame samples.

## Production integrated correction

Changed only `android-port/Runtime/Platform/AndroidTestDiagnostics.cs`:

- Capture `frameWindowStartScene` at the beginning of each normal sampling interval. Preserve original 5-second sampling cadence, frame-sample array, percentile sorting, `Time.unscaledDeltaTime`, `FrameTimingManager`, all existing HUD metrics, and original `scene=` key for old readers.
- Count active scene changes with a **static revision counter** in the original `private static void ActiveSceneChanged` callback. This preserves B12's existing callback/lifecycle contract. Track loaded/unloaded scene content revisions as well, including *additive* scene loads, with **no additional per-frame scene traversal**, allocations, JNI/Graphics API calls or setup hooks.
- Every new `performance/sample` reports `frame_window_start_scene`, `frame_window_end_scene`, `frame_window_active_scene_changes`, `frame_window_content_scene_events`, `frame_window_active_scene_stable` and `frame_window_content_stable`. A counted mixed-content window is **not** a stable benchmark window. These are informational fields: a single active scene does not imply matched world/viewpoint/quality or correct pixels.
- On existing Android pause/resume, reset only these provenance markers along with existing frame accumulators. The scene callbacks themselves **do not discard or reset frame samples**, so real loading stutters remain observable rather than silently hidden.

The first code commit temporarily used an instance callback and broke the historical B12 source-policy signature (`private static void ActiveSceneChanged`). That is a genuine test conflict; it was corrected by using a static revision counter, not by deleting B12 or weakening its test. The original B12 live coroutine remains registered, untouched and still compiles against its existing source harness.

Extended `tests/test_android_diagnostics_policy.py` to check that real frame sample aggregation is retained, transition bookkeeping is lightweight and annotated, the static callback ABI remains unchanged, and pause clears metadata.

## Analysis consumer now fails closed

Enhanced existing `scripts/t5_cl_unity_surface_bridge.py` and `tests/test_t5_cl_unity_surface_bridge.py` with conservative provenance parsing:

- Original owner phone logs lack all new fields: classify **`legacy_unlabeled`**. Do **not** reclassify their 36+116 valid Unity intervals as `tagged_stable_content`.
- Future logs with a complete, internally consistent six-field set are labeled `tagged_stable_content` or `tagged_mixed_loading`. A partial, contradictory, malformed or negative transition count is rejected instead of silently assumed stable.
- A positive `tagged_stable_content` observation is *still not* an A/B frame performance verdict until actual APK/OBB SHA, scene, camera/world state, graphics quality/render scale, pause/focus, temperature and shader error phase are aligned.

## CI evidence and scope

- [Original Android platform guard 42149741298](https://github.com/alwansan/raf/actions/runs/42149741298) completed success with first production C# code.
- [B12 scene shader snapshot CI 42149741343](https://github.com/alwansan/raf/actions/runs/42149741343) failed because its required static scene callback signature was changed. This was diagnosed from actual CI log. [Follow-up B12 CI 42150086078](https://github.com/alwansan/raf/actions/runs/42150086078) **SUCCESS** with restored static signature and identical bounded shader snapshot coroutine.
- [Android platform CI 42150116695](https://github.com/alwansan/raf/actions/runs/42150116695) **SUCCESS** on code + policy test commit `6284b099eefbd36c6ab6bd0fe7c8b374b1416e69`: diagnostics source policy **11/11 PASS**, including new scene-window test, and entire pre-existing platform workflow green. It compiles the netstandard offline platform lib, **not an Android Unity player**, and cannot prove actual runtime frames on device.
- [T5 genuine four-blob reader 42150565706](https://github.com/alwansan/raf/actions/runs/42150565706) tests new legacy/new-source provenance rule against the four existing authenticated CL sources and synthetic edge cases. Verify its final result before claiming it passed.
- No Unity rebuild, native APK/XAPK/OBB, original resources/shader/FFT, .meta/GUID, touch/layout, T5 scheduled Resolution, T1/T2/T3/T4 game code, Steam, FMOD, Settings or release modified. P0 WATER-001/RENDER-002 still open, PERF-007 open, full readiness NOT_READY 0/3.

## Required later game verification

After a coordinated signed Android test build, inspect a five-second performance window that spans Menu → MainScene and additive scene loads. Require the six new provenance fields; check the preserved frame count/FPS/p95 and true counts of active/content scene events. Then ensure new performance comparisons **exclude** mixed loading windows while retaining those windows separately for load-time performance analysis. Repeat with the same signed APK/OBB and identical world/graphics settings before making any numerical performance claim. This fixes source-side attribution only until actual Unity/phone observation is recorded.
