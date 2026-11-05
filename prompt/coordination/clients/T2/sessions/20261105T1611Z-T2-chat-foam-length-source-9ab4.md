# T2 chat — original Foam newarr RenderTexture[] length producer origin

- session_id: `20261105T1611Z-T2-chat-foam-length-source-9ab4`; origin `chat`; owner T2; WATER-001; status active.
- base_sha: `5c45d20d1112e18ca6a544bbcdaed7f1960db18a`. Work reserved before code under `prompt/coordination/work/WATER-001/T2-20261105T1611Z-T2-chat-foam-length-source-9ab4-length-source.json`, commit `68b50886e7aa150b86c53018c7c5e46169abcd93`.
- resumed_from_sessions: `20261105T1540Z-T2-chat-byref-target-b6af`, scheduled `20261105T1520Z-T2-scheduled-e7c1`.
- verified predecessor: original SHA-authenticated [CI42060338704](https://github.com/alwansan/raf/actions/runs/42060338704) proves same-block newarr UnityEngine.RenderTexture[] to exact typed ref formal stind.ref and stelem.ref through array loaded from same formal. [CI42060975715](https://github.com/alwansan/raf/actions/runs/42060975715) SUCCESS source confirms size operand is NOT immediate direct ldc.i4; original four index values are distinct/nonnegative but in-bounds unknown.
- experiment_key: `T2|original-ZIP2-15964ea8|DLL-0a6f0527|exact-RT-newarr-length-producer-local-arg-call|bounded-basicblock-v1`.
- intended files: own new `FoamByrefLengthOrigin.cs`, `Program.cs`, own `.github/workflows/raft-t2-foam-managed-literals.yml`, session/work/experiment/event. No original game assets, ShaderLab, .meta, settings/audio or postponed touch.
- question: which actual typed IL op produces newarr length, and if it comes from a local can a **same basic block** original local assignment prove its immediate origin? Fail closed on branches/unsupported opcodes; don't reveal private source names, IL or values. In-bounds verdict only if exact original literal size itself is source-proven.
- coordination: T1 FFT run `42061768669` active; scope different. No T2 original managed run active at reservation. No T1/T3/T4/T5 native/build cancellation.
- next: commit bounded source-authentic verifier + strict synthetic controls, execute CI and read only safe aggregate. WATER-001 OPEN / NOT_READY0/3.

## Source commit / original CI checkpoint

- Work reserved before source edits at `68b50886e7aa150b86c53018c7c5e46169abcd93`. [Commit 3b968223](https://github.com/alwansan/raf/commit/3b968223d951a380485024a7491d8f04ca01bd47) modifies only T2-owned new `FoamByrefLengthOrigin.cs`, `Program.cs`, and `.github/workflows/raft-t2-foam-managed-literals.yml`. Exact source SHA pinned unchanged.
- Source hypothesis: previous original `newarr` length not a direct `ldc.i4`; identify immediate producer category and one-hop same-basic-block `ldloc`/`stloc` provenance with fail-closed branch entry detection. Synthetic controls cover local constant, local from int argument, and branch-separated local (unknown).
- [CI42062967598](https://github.com/alwansan/raf/actions/runs/42062967598) `queued` at checkpoint; no original length origin claim yet. No original source values, IL, names or private hashes disclosed; prior source-authenticated newarr-to-ref store and element write CI42060338704 success remains valid.
