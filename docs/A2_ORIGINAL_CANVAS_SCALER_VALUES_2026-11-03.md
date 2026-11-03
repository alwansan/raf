# A2 — SHA-authenticated original CanvasScaler serialized values (3 November 2026)

**Client:** `raft-20261103T095700Z-a2b31f4d`; bounded issue `DISPLAY-003`. This is source and original serialized UI data recovery, **not** an Android runtime repair, a full Unity serialization TypeTree export, or installed-phone acceptance.

## Exact source and reproduction

- Original `Raft/Raft_Data/Managed/UnityEngine.UI.dll` Git blob SHA-1 `7c31ff89d8525add38b34f218666f6c9d8db0a58`, byte SHA-256 `5dcb24be77bf14930e38bfedafeb872a37bd09ce1d42e841b6a80cf6ba2e41ea`.
- Unity UI `CanvasScaler` temporary ILSpy decompilation SHA-256 `b7883dcab9148820aaf6e0f14d61ed2501fce2f26b4e791604528f6302d9e4e3`; decompiled source is **not** published. Exactly ten expected original UI scaler fields with types/order, plus separately authenticated trailing serialized `bool m_PresetInfoIsWorld` decorated `[SerializeField]`, after the ten. The three other in-class instance `m_` field declarations have no adjacent `[SerializeField]` marker.
- Original `globalgamemanagers.assets` Git SHA-1 `4eabb7cb093ead2f2b0c8f3451dd953a9f5ff0c9`; original scene `level0` Git SHA-1 `2aec4377058baf72656a2ba0daea9aefc67fcb7e`; original `level1` `1944f11673108f8db2084906ff5899003c97fc4a`. All three independently verified and never modified.
- Source files: `scripts/probe_a2_scaler_raw_shapes.py`, `scripts/probe_a2_scaler_value_decode.py`; synthetic unit fixtures in `tests/test_probe_a2_scaler_raw_shapes.py` and `tests/test_probe_a2_scaler_value_decode.py`; isolated workflow `.github/workflows/raft-a2-scaler-raw-schema.yml` (Ubuntu24.04, 10-minute cap, no LFS, no Unity, no Android, private ILSpy output).
- Latest source/test commit: [b83f51a1c1e9](https://github.com/alwansan/raf/commit/b83f51a1c1e921332d610d995db3fcb409255071). [Authentic original-source and scene CI41636519603](https://github.com/alwansan/raf/actions/runs/41636519603), job125918983831 **COMPLETED SUCCESS**: 8 synthetic field-metadata tests +8 synthetic decoder/base-pointer/enum/float/trailer-corruption tests; all original file Git SHA checks and seventeen original component records decoded with fail-closed validation.
- Earlier independent [CI41633458226](https://github.com/alwansan/raf/actions/runs/41633458226) **SUCCESS** on the initial ten-field metadata/17-record-size scan (6 checks). Intermediate CI attempts **failed on real code assumptions**: script pointer assumed at byte20 instead of original byte16; then the trailing serialized editor preset flag was initially unclassified; finally synthetic fixture/escaping mismatches. These were not passed off as game failures. [CI41635191374](https://github.com/alwansan/raf/actions/runs/41635191374) already passed for the provisional ten-field interpretation (7+7 checks), and final run adds authenticated 11th field and independent fixture negatives.

## Original binary layout verification

Every one of the **17 original CanvasScaler MonoBehaviours** has exactly **80 bytes** in its serialized object record. Original non-LFS scene hash pins and `m_Script` PPtr identity uniquely match UnityEngine.UI.CanvasScaler. On each record, original typed native MonoBehaviour fields agree with:

- **32-byte base header**, including GameObject PPtr at offset0, enabled/editor flag bytes, script PPtr at offset16 and empty object name length at offset28.
- **44 bytes of ten fields** at offset32, in original Unity UI C# source order, with valid finite values and bounded enum/scale constraints.
- **4-byte appended editor-preset bool** at offset76, after the ten expected settings: value false, with three zero alignment bytes. This correlates with the additional `[SerializeField] bool m_PresetInfoIsWorld` declaration in original `CanvasScaler` source, following the other ten fields.

No raw binary, object names, original source bodies or private materials were emitted. This is structural source+bytes corroboration; the Unity full native `CanvasScaler` custom TypeTree itself is **not independently recovered**.

## Authenticated original UI values

| Field | Original `level0` — four scalers | Original `level1` — thirteen scalers |
| --- | --- | --- |
| `uiScaleMode` | 1 = Scale With Screen Size (4/4) | 1 (13/13) |
| `referenceResolution` | **1920×1080** (4/4) | **1920×1080** (13/13) |
| `screenMatchMode` | 0 = Match Width Or Height (4/4) | 0 (13/13) |
| `matchWidthOrHeight` | **1.0** (4/4; match height) | **1.0** (13/13) |
| `scaleFactor` | **1.0** (4/4) | **1.0** (12/13); **0.6600000262** (1/13) |
| `referencePixelsPerUnit` | 100 | 100 |
| `physicalUnit` | 3 | 3 |
| `fallbackScreenDPI` / `defaultSpriteDPI` | 96 / 96 | 96 / 96 |
| `dynamicPixelsPerUnit` | 1 | 1 |
| `m_PresetInfoIsWorld` | false | false |

The distinct level1 scaleFactor at **0.66** is real original serialized **configuration**, not a newly demonstrated Android defect. Note that `scaleFactor` may be overridden by Unity's active UI scale-mode logic at runtime; no effective phone scale was measured.

## Engineering conclusion and next gate

This source-only experiment closes the previously **unknown original CanvasScaler numeric values** for these 17 scene-owned components. It does **not** close `DISPLAY-003`: no authenticated pointer path from the Settings menu's actual displayed panel/prefab to a particular CanvasScaler has been reconstructed, and no on-phone comparison of the effective viewport, anchors, safe-area, scale/width or landscape rotation was performed. A `matchWidthOrHeight=1` source value by itself is not proof of unintended width stretching and must not trigger a blanket Android override.

Next narrow engineering step: traverse source-authenticated original Settings MonoBehaviour serialized fields, scene/prefab pointers and UGUI event ownership to the actual panel/Canvas. Compare the linked original scaler's numeric configuration to the Android Settings path and only patch an established mismatch. Preserve left Mouse0/500ms, all external input, original quality, GUIDs, `.meta`, source content, existing release/signed recovery and task ownership.

**Status:** `DISPLAY-003 SOURCE_REVIEW_REQUIRED`; `WATER-001/RENDER-002/FFT-FORMAT-009` and further integration gates remain; no immutable native candidate, **NOT_READY / 0-of-3 full readiness reviews**. A2 did not start/stop existing native jobs or download LFS, run Unity, request APK/OBB/XAPK, edit game/UI runtime, alter CL or modify any scheduled task.
