Original file: Raft_Data/sharedassets0.assets
Original size (bytes): 115978112
Original SHA-256: 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets0.assets.recovered"
  sha256sum "../sharedassets0.assets.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
