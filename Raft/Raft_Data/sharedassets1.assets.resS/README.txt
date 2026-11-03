Original file: Raft_Data/sharedassets1.assets.resS
Original size (bytes): 388054288
Original SHA-256: 730c91dc3c9d23cc3053d5a8cd8fdb91f09635b96fa5d413e85dbb863b77b2da
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets1.assets.resS.recovered"
  sha256sum "../sharedassets1.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
