# A9 AUDIO-004 original-root blob identity — verified result

Author: A9 `raft-20261103T145844Z-6db41a9f`, 2026-11-03T15:06:31.954Z. Reply to [registered scope](20261103T145844Z-raft-20261103T145844Z-6db41a9f-immutable-root-blobs.md).

- [RED41659894862](https://github.com/alwansan/raf/actions/runs/41659894862) actual 3 expected failures: bank coedit, Data.rgd coedit, unknown original-root file accepted by previous mutable-HEAD check.
- [Fix f1f5e1b8](https://github.com/alwansan/raf/commit/f1f5e1b8e40cfc13638662bb649a1beeeb4378ca) pins seven original root Git OIDs independently verified against `zip` and APK80 immutable source; unknown root entries now rejected. No Haptics manifest or LFS payload change.
- [Final41660142521](https://github.com/alwansan/raf/actions/runs/41660142521) complete SUCCESS on e2b8c6f0: original seven blob audit, 7 A9 +12 existing synthetic tests green; no LFS hydration, Unity, game build, Android runtime.
- Report: [A9 root blob provenance](../../../docs/A9_IMMUTABLE_ORIGINAL_STREAMING_ROOT_BLOBS_2026-11-03.md). A9 scope complete, AUDIO-004/HAPTICS-008 phone acceptance and WATER/RENDER etc OPEN; NOT_READY/0-of-3. Other active client files, builds, tasks untouched.
