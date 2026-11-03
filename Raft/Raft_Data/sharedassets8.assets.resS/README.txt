Original file: Raft_Data/sharedassets8.assets.resS
Original size (bytes): 60258016
Original SHA-256: 256d78a74126ea679cfc57458a8cd2bfc012f89359de8373c4846d8e6f9df5b9
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets8.assets.resS.recovered"
  sha256sum "../sharedassets8.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
