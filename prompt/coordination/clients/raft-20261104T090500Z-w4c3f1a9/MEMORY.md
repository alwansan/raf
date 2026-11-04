# W4 - Android build/delivery repair memory

## Role / scope
Independent W4 agent authorized by the owner to edit code/resources/workflows, build and deliver APK/OBB/XAPK on `feature/android-native-port`. Older role restrictions that forbid Unity/APK work do not apply to W4.

## Session start (2026-11-04T09:05Z)
- Base SHA: `2008a5fb94d7df16bdcc1966a00955025e5fbded`.
- Live review: last full native runs `41795800392` (07:56Z) and `41741108965` (Nov 3 23:41Z) both fail at step 33 "Restore exact-name Unity 2021.3.45f2 built-in material and particle programs with original GUIDs":
  `ValueError: No exported built-in shader identities matched` with audit `matched_identities: 0, parseable_declarations: 142, shader_files: 142`.
- W1 lineage run `41799635147` (HEAD `2008a5fb`, 08:27Z) fails in `scripts/verify_export_lineage.py` with
  `RAFT_LINEAGE_MISMATCH {"actual_yaml_materials":1524,"traced_yaml_materials":1524,"missing_actual":1524,"unexpected_actual":1524,"different_shader_pointers":0}`.

## Root cause established (reference-type defect, not GUIDs)
- The trace records the exporter's own `MetaPtr` via `collection.CreateExportPointer(...)`. Ordinary materials are exported by `DefaultYamlExporter : YamlExporterBase` whose `ToExportType` is `AssetType.Serialized` (**2**); shaders/fonts use `BinaryAssetExporter` subclasses -> `Meta` (**3**).
- `verify_export_lineage.actual_graph` keyed material documents as `(anchor, meta guid, '3')` hardcoded, while trace keys carried `'2'` for materials -> every key missed (missing=all, unexpected=all, different_shader_pointers=0 because no common keys).
- A YAML document's reference type lives in the PPtrs pointing at it; it is not part of the document identity.

## Fix (this session)
- `scripts/verify_export_lineage.py`: added `document_key()` returning (file_id, guid) with reference type validated to {2,3}; normalized trace exports and actual documents; font-importer branch and mismatch report use normalized keys. Unknown types still rejected; no gate bypass.
- `tests/test_export_lineage.py`: added real-shape positive test (trace type 2 joins YAML document) and negative control (type 1 rejected).
- Local test runs: `test_export_lineage.py` 12/12 OK; `test_builtin_engine_ownership.py` 2/2 OK; `test_restore_builtin_shaders.py` 10/10 OK. Synthetic reproduction of the real signature now passes.

## Next
- Watch `raft-w1-export-lineage` on the fix commit; next gates are engine database read and "builtin restorer with engine inputs".
- Then wire the full build (`raft-unity-editor-android-import.yml`) engine ownership inputs (instrumented same-instance export trace + W1EngineDatabase + staged originals) so step 33 can pass on real data, then request a full native build.

## Local evidence cache (not committed)
- `/root/test/test/raft/Raft/Raft_Data` matches all 14 ZIP2 shader-owner pins byte-for-byte (verified 2026-11-04), so source-side reproduction needs no downloads.
