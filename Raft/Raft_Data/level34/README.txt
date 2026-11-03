Original file: Raft_Data/level34
Original size (bytes): 52351536
Original SHA-256: 6ebcf37fe3d2c07305d1b8091b0284c213537e860e0ff068d9d8ea0692c749d4
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../level34.recovered"
  sha256sum "../level34.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
