Raft zip2 (NO GIT LFS)
======================
Files larger than 45 MiB are represented by directories named after the
original file, containing part-00000, part-00001, ... and README.txt.
Every part is at most 45 MiB. Originals were not modified when uploading.

To restore the entire original Raft directory after cloning zip2:
  bash restore_raft.sh
This creates ../Raft-restored/, verifies SHA-256 and size for EVERY original file.
The manifest RAFT_FILE_MANIFEST.tsv lists paths, sizes, hashes and modes.

Example: Raft/Raft_Data/sharedassets0.assets.resS/part-00000 is one chunk,
not the original .resS file. Unity/tools should use Raft-restored, NOT the
split directory structure until it has been restored.
