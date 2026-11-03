Original file: Raft_Data/sharedassets34.assets.resS
Original size (bytes): 445291168
Original SHA-256: bccc9b1587d655ceab3b1bd2646f05adbf965ed772a1066102b817a1e8a2dcc0
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets34.assets.resS.recovered"
  sha256sum "../sharedassets34.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
