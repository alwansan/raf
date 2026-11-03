Original file: Raft_Data/sharedassets30.assets.resS
Original size (bytes): 545736336
Original SHA-256: 8d6aadec4952a4962b91ef790784f95e1986d60cdd980555b206b0f39a3b6b40
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets30.assets.resS.recovered"
  sha256sum "../sharedassets30.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
