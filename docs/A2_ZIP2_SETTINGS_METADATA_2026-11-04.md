# A2 — exact original Settings MonoScript and managed FieldDef schema, 4 November 2026

**Client:** `raft-20261103T095700Z-a2b31f4d`. **Issue:** `DISPLAY-003`, still **OPEN**. **Overall:** `NOT_READY / 0-of-3` immutable source readiness reviews. This is a bounded, CPU-only original-source investigation, not an Android Settings aspect fix, Unity runtime test, APK, OBB or XAPK delivery.

## Source-of-truth and exact reproducible input

Read-only owner-provided `zip2/Raft` pinned at [commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`](https://github.com/alwansan/raf/tree/15964ea8f246b6e076ce26b60931ee2e1a9a2385/Raft). Isolated sparse `actions/checkout`, `lfs:false` and `filter:blob:none`. Four small original ordinary Git objects independently verified at the runner:

| Original `Raft_Data` path | Exact Git blob SHA-1 |
| --- | --- |
| `Managed/Assembly-CSharp.dll` (3,211,776 bytes) | `fc9d4ba920a178fdb89c970d9d772a01051dadc6` |
| `globalgamemanagers.assets` | `4eabb7cb093ead2f2b0c8f3451dd953a9f5ff0c9` |
| `level0` | `2aec4377058baf72656a2ba0daea9aefc67fcb7e` |
| `level1` | `1944f11673108f8db2084906ff5899003c97fc4a` |

Private ILSpy `CSharp9_0` verifies original `Settings.cs` normalized SHA-256 `904c52b337fe951f711e2efc15bfafc4fc77f2a8d2cc9c5bee2f7d14075103ad`. Neither source code nor private assembly/scene bytes or field names are committed, logged or uploaded. There is **no** 7.79 GB ZIP2 content SHA verification, restoration of split files, LFS hydration or alteration of the existing `feature/android-native-port/Raft` tree.

## New code and exact test evidence

- `tools/a2-settings-metadata/Program.cs` plus `SettingsMetadata.csproj`: pinned `Mono.Cecil 0.11.6` metadata reader using Deferred mode to avoid resolving absent UnityEngine.CoreModule externals. Recursively enumerates original class and nested TypeDef candidates, records actual metadata `FieldDef` token sequence, custom `SerializeField`/exclusion flags and field-type families in a **temporary private JSON file** under `RUNNER_TEMP`.
- `scripts/probe_a2_settings_metadata_contract.py`: source SHA/size checks, exact MonoScript PPtr from native original scene0 and scene1 to the original global script registry, and then top-level (not nested) original `Settings` TypeDef full-name identity. Independently validates typed 32-byte native MonoBehaviour base pointers and original 612-byte Settings records. Reports only aggregate counts, booleans and fingerprints; no names/bytes.
- `tests/test_probe_a2_settings_metadata_contract.py`: synthetic-only negative controls for wrong namespace/assembly, duplicate or reordered FieldDef tokens, nested same-name Settings types, nonserialized/read-only fields, false source CSharp declarations and the pinned original 21/13/14 reconciliation.
- `.github/workflows/raft-a2-zip2-settings-metadata.yml`: independent Ubuntu24.04, max10min, no LFS, no native build, no release; private CSharp9, exact original managed metadata extraction and scene identity. Concurrency `cancel-in-progress:false`.
- [Code commit `243771a29db8d5227278f552274b5c3bab76fa2b`](https://github.com/alwansan/raf/commit/243771a29db8d5227278f552274b5c3bab76fa2b), [**CI #41737541506**](https://github.com/alwansan/raf/actions/runs/41737541506), job `126270493239`: **COMPLETED SUCCESS**, **10/10 synthetic tests**, all four SHA-pinned original source objects and both scene Settings script pointers verified. Earlier [CI #41736773796](https://github.com/alwansan/raf/actions/runs/41736773796) passed 7 tests and established the first exact metadata inventory; [CI #41737137816](https://github.com/alwansan/raf/actions/runs/41737137816) passed8 tests and identified the source parser's extra candidate. Intermediate failed CI were actual test-tool faults: an assertion-string mismatch, Mono.Cecil Immediate mode requiring absent UnityEngine assemblies, and mistakenly matching nested same-name Settings types; corrected with explicit negative controls. None are APK or phone failures.

## What is now proven

- Both authentic original scenes contain **one Settings MonoBehaviour instance each**, 612 bytes, resolving to the **same original MonoScript and exactly one top-level managed Settings TypeDef**. There are **16 managed types sharing the simple name Settings** and empty namespace (many are nested); they must not be confused with the top-level original script identity.
- Original top-level Settings TypeDef has **21 FieldDefs** in strict metadata-token order. **13 pass the current public/SerializeField/SerializeReference versus static, readonly, NonSerialized eligibility filter**. This is a *metadata eligibility filter*, not proof that all 13 are serialized by the full Unity engine.
- Of those 13: **6 same-original-assembly class** fields, **4 UnityEngine-prefixed type** fields, **1 other resolved external class**, **1 array of UnityEngine-prefixed elements**, **1 primitive type of four bytes or less**. Full external base-class/UnityEngine.Object inheritance and serialization of custom types still requires further resolution.
- Original privately recovered CSharp9 Settings text has **14 syntactic candidate field declarations**. All **13 metadata-eligible field names also appear in the source and in the SAME ORDER**. The remaining **one** is a source parser candidate with **no corresponding FieldDef at all**; it is not accepted as a 14th managed field. Pinned source-to-metadata contract on the exact original input is now enforced and regression-tested. Original ordered FieldDef kind/token signature SHA256: `96f669323870ff879c7728c401441b2f67a5a65268cb2eea61c4919b97161fa5`.
- Prior [original Settings raw-byte probe #41660274964](https://github.com/alwansan/raf/actions/runs/41660274964) found **48 overlapping raw local PPtr byte patterns** and at most45 disjoint 12-byte windows in each scene; these byte patterns are **not equivalent to the 13 metadata candidate fields** and never justified 48 typed pointer assertions.

## What is NOT proven / next safe engineering step

We still lack Unity's full original custom serialized Settings TypeTree, verified nested class field layouts and actual array element count/byte boundaries, and the **event/prefab/page reference path to the rendered Settings panel and its effective CanvasScaler**. The managed FieldDef order authenticates declarations but does not by itself establish Unity serialization offsets or actual Android landscape scaling behavior.

Next independently scoped step: use the exact validated 13-field token/type schema to resolve UnityEngine.Object inheritance, serializable nested custom classes and array element layout; parse the original 612-byte Settings objects conservatively with bounded pointer/array verification and cross-scene structural comparison. Only after the actual Settings canvas is established should any Android orientation/safe-area/UI scaling code be edited. Do not impose a global CanvasScaler override.

**Release/build boundary:** A2 did not run, schedule, cancel or alter Unity/APK/OBB/XAPK, Git LFS, original shaders/resources/materials, assets/.meta/GUID, CL, protected branches, other agents' workflows or the three existing scheduled tasks. `DISPLAY-003` and `WATER-001/RENDER-002/FFT-FORMAT-009` plus independent world/save/audio/device readiness gates remain OPEN, overall **NOT_READY, 0/3**.
