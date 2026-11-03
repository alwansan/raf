Original file: Raft_Data/level30.resS
Original size (bytes): 218100736
Original SHA-256: 5bfe6ed8ba29bfe41252b48a87679ec7402686dd1a73d353d24ed89f86c1abfc
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../level30.resS.recovered"
  sha256sum "../level30.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
