Original file: Raft_Data/sharedassets6.assets.resS
Original size (bytes): 95361248
Original SHA-256: 5fa2b99646a50762bef980fe4d3dcbba165e7a70aa9fbc4e710a5a9043c67995
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../sharedassets6.assets.resS.recovered"
  sha256sum "../sharedassets6.assets.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
