Original file: Raft_Data/level34.resS
Original size (bytes): 176287888
Original SHA-256: c46b77f26459eb73c0562539d29a370a57c8b213ab2cd71fb00ba974f5eab5e8
Chunk size: at most 45 MiB (47,185,920 bytes)

To restore all original Raft files (recommended):
  bash restore_raft.sh
The restored game will be created outside the Git repository as Raft-restored/.

To restore only this file, run from inside this chunk directory:
  cat part-* > "../level34.resS.recovered"
  sha256sum "../level34.resS.recovered"
Compare the SHA-256 with the value above. Do not confuse .recovered with the original path:
the original path is currently a directory containing chunks.
