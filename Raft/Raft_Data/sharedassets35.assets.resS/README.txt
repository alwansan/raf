Original file: Raft_Data/sharedassets35.assets.resS
Original size (bytes): 731390320
Original SHA-256: 0f0173194b389884b3733b833e2c23deafdde3d7d0274ad9f0be828c45e986d4
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets35.assets.resS.recovered"
  sha256sum "../sharedassets35.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
