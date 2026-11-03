Original file: Raft_Data/sharedassets36.assets.resS
Original size (bytes): 679414848
Original SHA-256: 3544faa8ad1aa1206dd7d01110444e45d97504885f61e58cabbc94e8eb714197
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets36.assets.resS.recovered"
  sha256sum "../sharedassets36.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
