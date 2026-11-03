Original file: Raft_Data/level30
Original size (bytes): 70435196
Original SHA-256: 53eb88c75c3a7d63333536e26b199dbfdcfd5ba8fb656ce843f24e45c3d9c94f
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../level30.recovered"
  sha256sum "../level30.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
