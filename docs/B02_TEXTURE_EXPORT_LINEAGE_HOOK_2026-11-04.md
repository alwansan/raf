# B02 — Optional original Texture2D export lineage from the pinned AssetRipper (4 Nov 2026)

**Agent/session:** B02 / 20261104T2233Z-B02-7c19. **P0 issue:** RENDER-002. **Branch:** feature/android-native-port only.

## Concrete integration gap

The already maintained [W1 same-export helper](../android-port/Experiments/ExportLineage/RaftExportLineage.cs) exclusively captures **classID 21 Material** and **48 Shader** in its existing `RAFT_PRIVATE_EXPORT_LINEAGE` JSON. B15's tested Texture2D sampler bridge and the B02 sRGB trace bridge require **classID 28 Texture2D** source/target pointer records; the original shared W1 trace therefore cannot feed those checks. Earlier synthetic-only B02/B15 trace tests did not close this upstream production data gap.

B02 added `scripts/b02_stage_texture_lineage.py`, a source-authenticated **staging-time tool** for that dependency. It refuses a W1 helper other than exact Git blob `8e64093f5d1cd283f34163e2527c414b3f86b7a7`, refuses ambiguous anchor positions, symlinks and existing targets, and writes a NEW staged .cs file using exclusive creation. It does **not** edit the committed W1 .cs file or main/native workflow.

The staged helper preserves the original Material/Shader capture exactly when only `RAFT_PRIVATE_EXPORT_LINEAGE` is set. The new optional `RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE` value names a private new file for class28 records. On the *same exporter invocation*, both outputs use one generated `export_instance` identifier. Each included Texture2D record has the original `asset.Collection.Name` and `asset.PathID` plus exporter-generated `MetaPtr(FileID, GUID, type)` from that exact collection. Duplicate original identities reject rather than silently merge; non-exportable Texture2D counts remain explicitly observable. Original textures/shader bytes themselves are never written into the trace.

## Reproduction and safety

The B02-only [compile workflow](../.github/workflows/raft-b02-texture-trace-compile.yml) checks out exactly pinned public AssetRipperCLI commit `036098ab525a3f9f693dc101edeb21faad4d32d8`, stages the modified helper in `RUNNER_TEMP`, calls the existing SHA-pinned `scripts.patch_export_lineage` on that *disposable public-tool checkout* and compiles the matching ExportLineage project with .NET9. It has an 18-minute cap, `ubuntu-24.04`, no original Raft game owner payload, no LFS hydration, no Unity Editor/Android build, no secrets, no uploaded private trace, and its own concurrency group with `cancel-in-progress:false`.

Test entry point: `python3 -m unittest discover -s tests -p test_b02_stage_texture_lineage.py -v` includes original-helper SHA, W1 class21/48 preservation, optional class28, same `export_instance` wiring, exclusive outputs, original file unchanged, wrong-source-pins, changed capture anchors, linked/occupied staging rejection, and no source object identity in stage summaries.

**Limitation:** A successful compile proves only the optional trace helper is source-compatible with pinned AssetRipper and synthetically staged safely. It does NOT prove an actual same-instance Raft texture trace has been produced, GUIDs were compared against a real export, render pixels match, or Android colors are corrected. The B02 importer guard remains READ-ONLY and `--repair` always refuses.

## Next evidence needed

Run one coordinated **real** export with source ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` authenticated and both private output env vars enabled, ensure private trace paths exist within the runner and are not artifacts. Pass the class28 trace to `scripts.b15_texture_sampler_parity` and `scripts.b02_texture_import_color_guard --trace --original` with matching actual export. Authenticate all source owner hashes, check class28 coverage and original/export ID pairing, report safe aggregate mismatch counts only; then perform Unity pixel checks before enabling any correction. Do not start another full Raft export solely to rerun existing W1 unless coordinated with its active workflow.

**Game status:** RENDER-002/WATER-001/LOCAL-005 remain OPEN, NOT_READY, immutable readiness reviews 0/3; APK86 is older than this source tool. Audio and Settings untouched, touch deferred.

## Verified final source-only compiler result

[B02 isolated CI41927712988](https://github.com/alwansan/raf/actions/runs/41927712988) **COMPLETED SUCCESS** from immutable source [477344ea3a903736761ffd4e9dd534604d08bc89](https://github.com/alwansan/raf/commit/477344ea3a903736761ffd4e9dd534604d08bc89), job126916385592. All **6/6** public-source staging negative cases pass. The exact Git-blob original W1 helper was verified, and the newly staged helper SHA256 is `c99c6e163ee20d9ff72e2180ed72ce94b5c608e20dc1095c3c81d3e678532c1e`. Pinned upstream AssetRipperCLI was patched in runner temp, .NET9 compiled, published and the program's `--probe-tool` smoke test returned SUCCESS. No AssetRipper package change was committed. No game data was mounted, no texture objects were actually exported; **original texture source=0, real trace=0, Unity/Android pixel=0** as explicitly logged.

Independent earlier [B02 importer/trace bridge CI41927008905](https://github.com/alwansan/raf/actions/runs/41927008905) passed **16/16** at source `ee12d1c349167e7012a8cee7ea1f8d9e8adb4c75`, including strict nested `TextureImporter.mipmaps.sRGBTexture` and in-memory re-use of B15's source→export GUID mapping. That test was synthetic and did **not** supply a real source+export pair. This trace compiler adds the previously missing actual exporter **capture mechanism** but not an end-to-end Raft export test.
