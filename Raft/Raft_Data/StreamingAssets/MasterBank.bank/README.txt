Original file: Raft_Data/StreamingAssets/MasterBank.bank
Original size (bytes): 101600960
Original SHA-256: 10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../MasterBank.bank.recovered"
  sha256sum "../MasterBank.bank.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
