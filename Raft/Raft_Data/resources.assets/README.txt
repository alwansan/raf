Original file: Raft_Data/resources.assets
Original size (bytes): 111533516
Original SHA-256: 87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../resources.assets.recovered"
  sha256sum "../resources.assets.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
