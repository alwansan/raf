Original file: Raft_Data/sharedassets36.assets
Original size (bytes): 110149324
Original SHA-256: b32fcd9d327c8926b2309ffc1b5645a0c23d64ed95be37ed94e96f34736530c8
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets36.assets.recovered"
  sha256sum "../sharedassets36.assets.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
