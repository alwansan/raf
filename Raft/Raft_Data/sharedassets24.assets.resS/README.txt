Original file: Raft_Data/sharedassets24.assets.resS
Original size (bytes): 301743760
Original SHA-256: 6773fa70927c1030e0006928e9578feb0447dd6cb0db0407500b3cd803d1fe1b
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets24.assets.resS.recovered"
  sha256sum "../sharedassets24.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
