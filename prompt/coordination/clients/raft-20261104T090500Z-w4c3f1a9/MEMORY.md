# W4 - Android build/delivery repair memory

## Role / scope
Independent W4 agent authorized by the owner to edit code/resources/workflows, build and deliver APK/OBB/XAPK on `feature/android-native-port`. Older role restrictions that forbid Unity/APK work do not apply to W4.

## Session start (2026-11-04T09:05Z)
- Base SHA: 2008a5fb94d7df16bdcc1966a00955025e5fbded.
- Full native runs 41795800392 and 41741108965 both failed at step 33 "Restore exact-name ... built-in ... programs" with `matched_identities: 0` (no loose builtin files; the gate was added after the last green build and had never passed).
- W1 lineage run 41799635147 failed in `verify_export_lineage` with all-keys-miss (1524/1524) though counts matched.

## Root cause established (reference-type defect, not GUIDs)
- Trace records the exporter's own MetaPtr via CreateExportPointer. Materials use DefaultYamlExporter (ToExportType = Serialized, 2); shaders/fonts use BinaryAssetExporter (Meta, 3). The verifier hardcoded '3' for material documents, so every key missed.
- A YAML document's reference type lives in the PPtrs pointing at it, never in the document.

## Fixes landed (all validated)
- `scripts/verify_export_lineage.py` + `tests/test_export_lineage.py` (75e9f0e2/a2259067): document_key() joins on (anchor fileID, asset GUID) with reference type validated to {2,3}; unknown types rejected; no bypass. **raft-w1-export-lineage 41804737856 SUCCESS**: 1544 material edges, 225 shaders, 1524 documents, 14 implicit fonts, 8 engine redirects; engine ownership 743 refs / 11 pointers.
- `android-port/Experiments/ExportLineage/Program.cs` (ca70704d): prints effective `ScriptExportMode: Decompiled` and the CLI-equivalent `=== COMPLETED ===` marker so the existing script-import verifier accepts the instrumented host. Re-validated by 41807302060 SUCCESS.
- `.github/workflows/raft-unity-editor-android-import.yml` (5e28572b): replaces the release binary with the pinned source-instrumented exporter (patched at run time, trace kept private), stages authenticated engine resources into the export input, adds the W1EngineDatabase step, and moves the builtin ownership gate to the pristine export boundary with all four engine inputs. Aux workflows green.

## Policy note
- W1 handoff W1_OWNER_FULL_BUILD_ATTEMPT_2026-11-04 states both strict builtin/water gates are unchanged and the water verifier cannot be cleared by pass-count-only stubs. Do not bypass the water gate without owner direction; report the demonstrated blocker instead.

## Next
- Triggered experimental full build from 5e28572b; expected frontier: strict water gate (last pre-run report: shaders all 1-pass, computes=0, `authentic_water_kernel_identity_verified` hardcoded false).
- If water blocks, continue with authentic recovery or an owner-directed lane decision.
## Result 09:57Z - full build 41808015938
- Instrumented full export + script-import fidelity passed (managed_provider_count 151).
- **Builtin ownership gate passed for the first time** on the full export: 750 refs / 11 pointers / 1544 edges / 1536 documents, `changes_to_project: 0`.
- Run then stopped at the unchanged strict water gate: VolumetricLight 5/5 OK, Depth Copy 9/4 OK, Water Spectrum 1/6, Foam 1/2, Blur 1/2, water compute candidates 0, identity flag false.
- No APK/OBB/XAPK; NOT_READY 0/3. Next work is authentic water pass/compute recovery (A12/A1 lane), not a gate change.
- Report: docs/W4_BUILTIN_GATE_AND_WATER_FRONTIER_2026-11-04.md

## Local evidence cache (not committed)
- `/root/test/test/raft/Raft/Raft_Data` matches all 14 ZIP2 shader-owner pins byte-for-byte (verified 2026-11-04), so source-side reproduction needs no downloads.
