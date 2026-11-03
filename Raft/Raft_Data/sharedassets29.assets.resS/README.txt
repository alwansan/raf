Original file: Raft_Data/sharedassets29.assets.resS
Original size (bytes): 295782704
Original SHA-256: 03f8af3b413488fbd704e1360bf58e879fe8516822b221a08b273c45edbac7f3
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets29.assets.resS.recovered"
  sha256sum "../sharedassets29.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
