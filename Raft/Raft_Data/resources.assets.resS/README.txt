Original file: Raft_Data/resources.assets.resS
Original size (bytes): 538497440
Original SHA-256: 29e6f3edc12be65e99003f27b90c32779c91d6a66f9ee169ce6bd2386e531f87
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../resources.assets.resS.recovered"
  sha256sum "../resources.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
