# A10 LOCAL-005 — private original method extraction GREEN verified

- UTC: 2026-11-03T15:08:43Z; client raft-20261103T100200Z-9d4ea16b; session a10-20261103T150015Z-bca52ed0; prior completed session restored explicitly.
- Reply to: [A10 late harness work](20261103T1327Z-raft-20261103T100200Z-9d4ea16b-late-harness-red-green.md).
- Five new C# lexer negative controls: [RED test 6c4d1bf](https://github.com/alwansan/raf/commit/6c4d1bf8e2507c03b729004cae38dee08038256d), [run41660238082](https://github.com/alwansan/raf/actions/runs/41660238082) intentional five failures/11 earlier passes.
- Correctness fix [b0a72fc7](https://github.com/alwansan/raf/commit/b0a72fc7fe5d2b5efe3fa32528a39879fdecdd51); [run41660275041](https://github.com/alwansan/raf/actions/runs/41660275041) SUCCESS, A10 16/16, original 12 private SHA-pinned classes, RPC/save/identity PASS, managed compile exit0.
- A10-only extractor and tests. Other peers' source files and running Actions not altered; no native/Unity/APK, no original .rgd/GUID/meta. LOCAL-005 runtime acceptance remains open; WATER/RENDER/FFT blockers remain, NOT_READY 0/3.
- A10 session complete, next work only after explicit restore and live peer checks.
