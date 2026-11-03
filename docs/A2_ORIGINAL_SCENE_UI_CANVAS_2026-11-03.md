# A2 — Authenticated original scene UI/CanvasScaler relationship (3 November 2026)

**Issue:** DISPLAY-003; client `raft-20261103T095700Z-a2b31f4d`. This is a CPU/source asset structure investigation, **not** an Android aspect repair, Unity import, GPU result, or phone test.

## Source and reproducible CI

- [Initial probe commit 8feac3e](https://github.com/alwansan/raf/commit/8feac3e6921f260ab5098a4e77d6279a3883bc3e), [CI41628388766](https://github.com/alwansan/raf/actions/runs/41628388766) **SUCCESS**: 8 synthetic tests; six original ordinary Git scene blobs `level0..level5` match their hardcoded Git object hashes.
- [Native-transform ancestry commit 0a2eee0](https://github.com/alwansan/raf/commit/0a2eee0dcf0c9ea73ded43f1c744e82f195541dc), [CI41628772940](https://github.com/alwansan/raf/actions/runs/41628772940) **SUCCESS**: 11 synthetic tests; counts and parent-chain categories from authentic scenes.
- [MonoScript identity probe commit 86bd9a0](https://github.com/alwansan/raf/commit/86bd9a0ec84df9f9764b649680d11478afabcf59), [CI41629163061](https://github.com/alwansan/raf/actions/runs/41629163061) **SUCCESS**: 11 scene + 5 script synthetic tests; original non-LFS `globalgamemanagers.assets` Git blob `4eabb7cb093ead2f2b0c8f3451dd953a9f5ff0c9` verified.
- [Final CanvasScaler ancestor probe commit db9ba86](https://github.com/alwansan/raf/commit/db9ba867619a67bbb05f047fcf17fddd632dfbb2), [CI41629641835](https://github.com/alwansan/raf/actions/runs/41629641835), job125895634545: **COMPLETED SUCCESS**. 11/11 scene plus 7/7 MonoScript negative controls; all original scene/script Git fingerprint checks and private object scans passed.

The probes run on Ubuntu24.04 without Unity Editor, APK or LFS hydration. Original serialized asset bytes, Unity object names, script payloads, raw fields and unredacted source are **never** committed, uploaded as artifacts, or printed.

## Authenticated structural findings

| Original source | Native Canvas | Native RectTransform | Objects with Settings-like names | Original CanvasScaler scripts attached to native Canvas owners |
| --- | ---: | ---: | ---: | ---: |
| `level0` (Git `2aec4377058baf72656a2ba0daea9aefc67fcb7e`) | 4 | 1,644 | 2 | 4 |
| `level1` (Git `1944f11673108f8db2084906ff5899003c97fc4a`) | 56 | 3,033 | 1 | 13 |
| `level2..level5` | 0 | 0 | 0 | Not inspected for script links |

`level0` contains 750 stretch-anchored and 894 fixed-anchored RectTransforms; `level1` contains 1,135 stretch and 1,898 fixed. The original global script owner contains **3,827 MonoScript objects**, including a script uniquely matching class `CanvasScaler`, namespace `UnityEngine.UI`, assembly `UnityEngine.UI`. Scene0 has **4**, scene1 **13** MonoBehaviours whose typed script PPtrs resolve to this authenticated Unity UI script; all 17 share the GameObject with a native Canvas. This corrects a misleading negative inference from the earlier generic MonoBehaviour typetree inventory.

A distinct **class-name-only** `Settings` script PPtr is attached to a Settings-named GameObject in each of `level0` and `level1` (one match per scene). On verified *in-scene native Transform ancestor chains*, neither of these script-bearing Settings GameObjects has a verified CanvasScaler ancestor. In `level0`, a different Settings-named GameObject does lie under native Canvas ancestry; script-bearing and Canvas-ancestry-named objects must **not** be conflated. This does **not** prove an absent CanvasScaler for the displayed Settings menu: it might be reached by separate object references, panels, prefabs or runtime composition.

## Remaining unknowns and next engineering gate

- **CanvasScaler custom serialized values are NOT decoded**: `referenceResolution`, `uiScaleMode`, `screenMatchMode`, `matchWidthOrHeight` are unknown. All 7,508 MonoBehaviours in scene0 and 5,928 in scene1 exposed only their generic base-field typetree via UnityPy; presence/absence of scaler settings cannot be inferred from base fields.
- No authenticated Settings widget-to-prefab dependency closure, UI event call graph, Android screen-size/orientation numeric comparison, or real Unity/phone execution.
- The earlier original `ControlsSettingsBox.sizeDelta` write at line110 was authenticated by [CI41623586923](https://github.com/alwansan/raf/actions/runs/41623586923), but **its target is not yet linked** to a scene canvas or to the user's visual regression.
- Next independent work: recover authentic per-CanvasScaler custom serialized field schema/values with exact MonoScript identity, correlate active Settings page and orientation. Reject guessed bytes/layout; only change runtime on a proven mismatch. Avoid a broad CanvasScaler override or global screen-resolution clamp.

**Status:** DISPLAY-003 **SOURCE_REVIEW_REQUIRED**. WATER-001/RENDER-002 and other source gates remain; full immutable candidate reviews **0/3**, overall **NOT_READY**. No new Unity/APK/OBB/XAPK build, release, native request, LFS download, .meta/GUID alteration, gameplay/touch fix, CL write or scheduled-task edit was made by A2. A separate full-native run already existed and was neither initiated nor interrupted by A2.
