# A9 — immutable original StreamingAssets root blob identities (3 Nov 2026)

## Scope and provenance

Resumed completed A9 chain as independent `raft-20261103T145844Z-6db41a9f`, session `A9-20261103T145844Z-91c65a3f`. Current branch `feature/android-native-port` only. Verified original seven tracked non-Haptics root Git blobs have **exactly identical SHA1 Git blob objects** in original owner `zip` branch, immutable older APK80 source `9462f8edd8cdb5becbccb96521f2876ef9924410`, and current development branch before editing; no LFS hydration required to inspect Git object IDs. A5 already separately anchors the 29 Haptics WAVs through an immutable manifest blob SHA. Existing MasterBank.bank still requires original LFS size/SHA256 101600960 / 10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339 in production staging.

## Source defect and repair

The source checker previously compared non-LFS VO banks, `Data.rgd` and config to their Git blob OIDs **from the same mutable HEAD**, which accepts accidental content+HEAD co-edits and stages changed game data as though original. A separate unrecognized file newly tracked under the original source root was likewise staged, because the workflow only required a minimum set of bank filenames.

[RED commit a2211406](https://github.com/alwansan/raf/commit/a22114063e2c757fbe685fc1ec33c7569bcfaaf4) and [CI41659894862](https://github.com/alwansan/raf/actions/runs/41659894862) intentionally FAILED exactly **3 new synthetic controls**: co-edited committed VO bank, co-edited committed `Data.rgd`, unknown committed root file; all failed with `ValueError not raised`, confirming actual acceptance by the old source.

[Production fix f1f5e1b8](https://github.com/alwansan/raf/commit/f1f5e1b8e40cfc13638662bb649a1beeeb4378ca) adds `ORIGINAL_ROOT_BLOB_SHAS` containing seven fixed original Git SHA1 object identities. Before copying, it now rejects any unknown root file or mismatched original-root OID, even if altered source and HEAD agree. Haptics retains its separate independent manifest trust check. No payload bytes, `.meta`, GUIDs, serialization, filenames or bank order changed. Synthetic tests patch only their fixture-local root pins; no production CLI bypass.

[GREEN source CI41660031718](https://github.com/alwansan/raf/actions/runs/41660031718) **SUCCESS**: 7/7 A9 tests (4 previous +3 new), 12/12 original staging fixture tests. [Final workflow commit e2b8c6f0](https://github.com/alwansan/raf/commit/e2b8c6f081c9500d95b47b954c86c3fd565efd62) runs an additional no-LFS authenticated checkout assertion on all seven root Git blobs; [final CI41660142521](https://github.com/alwansan/raf/actions/runs/41660142521) **COMPLETED SUCCESS**, job126000873511: `ORIGINAL_ROOT_BLOB_PASS count=7 original_bytes_unchanged=true lfs_hydrated=false`, 7/7 +12/12 synthetic cases. Existing A5 Haptics and A9 atomic stage behavior preserved.

## Limits and next action

Seven Git object identities are anchored to the supplied original ZIP and immutable old source, but this does **not** execute Unity, verify hydrated MasterBank bank bytes in this no-LFS workflow, run a packaged OBB or prove audible FMOD/real phone world loading. Synthetic staging fixture is tiny (35 files, 1700 bytes). A hostile edit of verifier code and pins together is outside this accidental-coedit guard. Project `NOT_READY`, full immutable-candidate reviews `0/3`; AUDIO-004/HAPTICS-008 and WORLD/LOCAL-005, WATER-001, RENDER-002 remain open. A9's scoped task is complete only. Next responsible work: once authentic resource/render prerequisites close, coordinator-owned full package / mounted OBB and phone audio/world validation. No native Unity/APK/OBB/XAPK, release, scheduled task, CL write, LFS hydration, protected branch edits or build request was initiated by A9.

UTC verification checkpoint: 2026-11-03T15:06:31.954Z.
