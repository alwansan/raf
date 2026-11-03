Original file: Raft_Data/sharedassets13.assets.resS
Original size (bytes): 82942832
Original SHA-256: c0ed7662c41ae65b2d0477c1e08002963c2c26c13fbe9ad935a6d7e59a282591
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets13.assets.resS.recovered"
  sha256sum "../sharedassets13.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
