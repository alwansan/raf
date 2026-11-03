# A2 — original ZIP2 Settings source-backed type inventory (4 November 2026)

**Client:** `raft-20261103T095700Z-a2b31f4d`, issue `DISPLAY-003`. **Scope:** source-only CPU engineering, not an Android Settings aspect fix, Unity Editor build or phone test.

## Owner-provided complete original game provider

Immutable ZIP2 Git commit: [`15964ea8f246b6e076ce26b60931ee2e1a9a2385`](https://github.com/alwansan/raf/tree/15964ea8f246b6e076ce26b60931ee2e1a9a2385/Raft), read-only. The source provider is documented in [ZIP2_SOURCE_PROVIDER.md](ZIP2_SOURCE_PROVIDER.md). This experiment uses the **original small ordinary Git files only** via isolated `actions/checkout` with `filter: blob:none`, sparse paths, and `lfs:false`:

| Source (relative to ZIP2 Raft_Data) | Authenticated Git blob SHA1 |
| --- | --- |
| `Managed/Assembly-CSharp.dll` (3,211,776 bytes) | `fc9d4ba920a178fdb89c970d9d772a01051dadc6` |
| `globalgamemanagers.assets` | `4eabb7cb093ead2f2b0c8f3451dd953a9f5ff0c9` |
| `level0` | `2aec4377058baf72656a2ba0daea9aefc67fcb7e` |
| `level1` | `1944f11673108f8db2084906ff5899003c97fc4a` |

All four ordinary Git blobs were checked on the actual runner and matched the earlier authenticated A2 source records. **No complete 7.79 GB ZIP2 content verification is claimed**; no split files were fetched/reassembled, no LFS operation performed, and no existing `feature/android-native-port/Raft` source tree overwritten. Only the original managed DLL and tiny scenes were needed for this bounded task.

## Source/test implementation and witnessed CI

- Source-only original `Settings.cs` CSharp9 normalized SHA256 `904c52b337fe951f711e2efc15bfafc4fc77f2a8d2cc9c5bee2f7d14075103ad` verified in private CI. Decompilation and names were never published.
- `scripts/probe_a2_settings_typed_fields.py` extracts only top-level declaration types from a SHA-verified original Settings class while masking comments/string literals. Excludes static/readonly/const, explicitly nonserialized, and private fields lacking SerializeField. Reports broad type families, not field names or source bodies. Its source order is **a candidate**, not a Unity serialization token/offset guarantee.
- `tests/test_probe_a2_settings_typed_fields.py` negative-controls comments, string spoofing, nested methods/properties, private/static fields, arrays, enum/struct source family detection and incorrect class/brace input.
- `.github/workflows/raft-a2-settings-zip2-typed-fields.yml` uses Ubuntu24.04, CPU-only 10-minute timeout, independent concurrency group, optional private ILSpy CSharp9, exact pinned ZIP2 sparse checkout, `UnityPy==1.23.0`. **No original assets, binaries, decompiled code or logs with private game data uploaded.**
- [First original-source SHA-verified CI41731775311](https://github.com/alwansan/raf/actions/runs/41731775311) **SUCCESS** (6 synthetic tests, exact ZIP2); [catalog matching CI41732187637](https://github.com/alwansan/raf/actions/runs/41732187637) **SUCCESS** (6 tests); [declaration-family CI41732807830](https://github.com/alwansan/raf/actions/runs/41732807830) **SUCCESS** (7 tests); [final source `a2455448`](https://github.com/alwansan/raf/commit/a2455448194317481a60a7199d932f85d2c2014f), [**CI41733061252**](https://github.com/alwansan/raf/actions/runs/41733061252) **COMPLETED SUCCESS** (7 synthetic tests and exact ZIP2 original source reverified). An earlier synthetic-test lower-length restriction (CI41731684797) was repaired before these passes. An intermediate CI41732159476 ran without a newly needed optional UnityPy dependency; the final pinned dependency corrected this. Failed interim CI are not real game failures.

## Authenticated Settings source type findings

Original `Settings.cs` yielded **14** *candidate Unity-serializable field declarations* in its own class scope. These are 14 **declarations**, not 14 verified runtime Unity PPtrs:

| Family | Count |
| --- | ---: |
| Known Unity native object reference type declarations | 4 |
| Custom game/external type declarations, inheritance/serialization not fully resolved | 8 |
| Array or generic collection declaration with unverified element type | 1 |
| Built-in 4-byte scalar declaration | 1 |

Of the eight custom type declarations, **six class names** match exact original `Assembly-CSharp` MonoScript records in authenticated `globalgamemanagers.assets`. The other two are not matched there; original-private CSharp source-family lookup could not uniquely identify them, nor the collection element family. This does **not** establish six valid serialized offsets; name-only matches do not resolve namespace or a complete Unity TypeTree. The leading single built-in scalar is a **4-byte primitive**, not a serialized string.

The prior [A2 raw Settings pointer interval experiment CI41660274964](https://github.com/alwansan/raf/actions/runs/41660274964) found 48 aligned local pointer *byte patterns* per 612-byte Settings MonoBehaviour record but only **45 maximum nonoverlapping candidate windows** (44 universal across maximal choices). These structural candidate windows must **not be conflated** with the 14 actual source declarations: a single field may hold an array of many elements or a nested serializable value, and overlapping raw bytes can fabricate matches.

## Engineering decision and next step

A reproducible **ZIP2 original data acquisition path** for A2 is now proven without LFS. Original Settings field *type families* are narrowed, but exact **field metadata token order, custom type inheritance, nested collection serialization, 612-byte record boundaries and active Settings prefab/UI panel to CanvasScaler path remain unknown**. Do not claim a completed Settings aspect repair or set all Android CanvasScalers to match-height. Next scoped engineering work should extract managed metadata field order and resolved collection element serialization privately, reconstruct exact PPtr boundaries with negative controls, then prove the live Android panel/Canvas ownership before making a narrow runtime fix.

**Project status:** `DISPLAY-003` OPEN/SOURCE_REVIEW_REQUIRED; `WATER-001/RENDER-002/FFT-FORMAT-009` and other source/native gates remain; owner readiness **NOT_READY / 0-of-3 full independent reviews on unchanged candidate**. A2 did not alter original game source, material/shader resources, Unity assets/.meta/GUIDs, input/multiplayer, releases, CL or scheduled tasks and did not initiate, cancel, or claim Unity/APK/OBB/XAPK results.
