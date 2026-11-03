Original file: Raft_Data/sharedassets25.assets.resS
Original size (bytes): 217498752
Original SHA-256: cee00266ec286c506b1e2b2689fb8cec16213efe1463638058786b830d4ffc84
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets25.assets.resS.recovered"
  sha256sum "../sharedassets25.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
