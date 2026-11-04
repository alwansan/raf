# W4 — builtin ownership gate passes; strict water gate is the live frontier (4 November 2026)

Live run: [41808015938](https://github.com/alwansan/raf/actions/runs/41808015938), request commit `6ed699ca8d7b3cca7a0e6c460bbeebaade258abe`, reconstruct job 126500028449, 09:30–09:54Z. This attempt went further than every previous post-APK80 run and stopped at exactly one unchanged gate.

## What changed (all validated)

1. **Same-instance material document identity fix** — `scripts/verify_export_lineage.py` + tests: the trace records `AssetType.Serialized` (2) for `DefaultYamlExporter` materials while the verifier keyed material documents with a hardcoded type 3, so every key missed (1524/1524). Documents are now joined on (anchor fileID, asset GUID) with the trace reference type validated to {2,3}; unknown types are still rejected. [W1 lineage 41804737856](https://github.com/alwansan/raf/actions/runs/41804737856) **SUCCESS** (bounded pipeline).
2. **Full build wiring** — commit [5e28572b](https://github.com/alwansan/raf/commit/5e28572badf38b3e09693f875d1f18aff6e4432d) in `raft-unity-editor-android-import.yml`: the pinned public exporter is patched and built in-run (`patch_export_lineage` + typed host) and used for the project export with the private same-instance trace; the two authenticated engine resource providers are staged into the export input; the exact embedded engine database is re-read; and `restore_builtin_shaders` runs at the **pristine export boundary** with all four engine inputs (originals, trace, private database, reader summary). The old post-restorer invocation was removed. No authenticity bypass; strict water gate untouched.
3. **Instrumented host** — `Program.cs` reports the effective `ScriptExportMode: Decompiled` and the CLI-equivalent `=== COMPLETED ===` marker so the existing script-import fidelity verifier accepts the typed host.

## Evidence from run 41808015938

- Export + script import (step 19): `RAFT_SCRIPT_IMPORT_FIDELITY {decompiled_script_export: true, export_completed: true, managed_provider_count: 151, layout_mismatch_lines: 0, unknown_backend_fallback: false}`.
- Builtin gate (step 21) — **first pass ever**: `RAFT_BUILTIN_EXPORT_MATCH_AUDIT {matched_identities: 0, shader_files: 140, parseable_declarations: 140}` followed by `RAFT_BUILTIN_ENGINE_OWNERSHIP {engine_owned_shader_references_verified: true, source_mapped_internal_references: 750, source_mapped_unique_engine_pointers: 11, source_material_edges_verified: 1544, source_shader_objects_traced: 225, actual_material_documents_verified: 1536, changes_to_project: 0}`.
- Water gate (step 38) — the live frontier, unchanged and honest:
  - `Sandbox/VolumetricLight`: satisfied (5 passes) — authenticated restore step.
  - `UltimateWater/Depth/Depth Copy`: satisfied (9 passes) — W1 staged reconstruction.
  - `UltimateWater/Spectrum/Water Spectrum`: **1 of 6** passes.
  - `UltimateWater/Foam/Global`: **1 of 2** passes.
  - `UltimateWater/Utilities/Blur (Subsurface Scattering)`: **1 of 2** passes.
  - Water/FFT-named compute sources with kernels: **0**; `authentic_water_kernel_identity_verified: false`.
  - `RAFT_EXPORTED_RENDER_CONTRACT shaders=140 source_pass_histogram={1: 140} computes=0`.

No APK/OBB/XAPK was produced; NOT_READY 0/3. The strict gate was **not** modified or bypassed.

## Next work (recovery, not gate edits)

1. Authentic pass-graph reconstruction and installation for **Water Spectrum (≥6)**, **Foam/Global (≥2)** and **Blur (≥2)** using the same authenticated approach proven for Depth Copy and in progress for Blur (A12): original serialized parsed form + authenticated DXBC programs, no fabricated passes.
2. Authentic water/FFT `.compute` staging with identity attestation (A1's CPU numeric translation proof exists; staging and identity verification do not).
3. Then the strict water gate can pass on its own terms. Do not toggle `authentic_water_kernel_identity_verified` without that restoration.

## Scope limits

- The builtin ownership proof is a same-instance export-trace proof, not a Unity compile, GPU execution or device test.
- The water gate is a structural source check; passing it will still require Unity import and phone evidence.
