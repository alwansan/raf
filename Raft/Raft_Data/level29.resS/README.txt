Original file: Raft_Data/level29.resS
Original size (bytes): 97397152
Original SHA-256: be1b1f3c6532c57c588b8851b5908a7aaf28a6cc8d97cb88a2339ec737d1f686
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../level29.resS.recovered"
  sha256sum "../level29.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
