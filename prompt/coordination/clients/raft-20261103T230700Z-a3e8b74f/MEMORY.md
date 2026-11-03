# A3 continuation — RENDER-002 vendor shader restoration transaction

Identity `raft-20261103T230700Z-a3e8b74f`, session `a3-20261103T230700Z-c64da0f2`, resumed from completed prior A3 `raft-20261103T224800Z-a3c41e7b`. Latest branch HEAD at registration `f6adf9361999146c730f1d8b6b959dcb59c0977a`. Live coordination, owner requirements, ZIP2 provider, prior A3 work, render workflow CI, shader restorer source and tests reviewed. This scope does not overwrite other agents W1 builtins/FFT, A12 Blur, W2/W3 materials, or A14 GUID work.

Original shader recovery has known partial failure mode: shared `scripts/restore_tmp_shaders.restore` is invoked by TMP/PostFX/Volumetric and opens destination includes/fallback assets for writes without a rollback list, follows symlinked Assets parent directories, and creates a backup with no comprehensive failure cleanup. Scope: source-level transactional restoration and path safety so original shader programs and .meta GUID bytes survive an interrupted restore, without inventing any shader programs or visual success.

Register before editing. Next: synthetic RED at real source, surgical GREEN fix, original three vendor restorer test sets and isolated GitHub CI. Do not start native Unity/APK/Release or read LFS/ZIP2 payloads.
