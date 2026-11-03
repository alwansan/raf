Original file: Raft_Data/sharedassets0.assets.resS
Original size (bytes): 1779131136
Original SHA-256: 9169e628e6e7c6fcadfc20e8eae92218f9edbb33c573f6cc474f532437b50ff8
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets0.assets.resS.recovered"
  sha256sum "../sharedassets0.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
