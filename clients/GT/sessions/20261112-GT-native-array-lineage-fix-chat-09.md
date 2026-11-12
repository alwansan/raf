# GT — Chat-09: native ClassID187 private lineage root-cause correction

- session_id: GT-20261112-CHAT-09-NATIVE-LINEAGE-FIX
- origin: chat; agent: GT
- writable branch: `feature/android-native-port` only
- pristine original source: `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385` with manifest SHA256 and size, **no LFS**
- no writes to `main`, `zip2`, game original data, source `.meta`, or T1–T5 restricted gates

## Real checks

- [43150158897 PASS](https://github.com/alwansan/raf/actions/runs/43150158897): full isolated SHA-authentic ZIP2 → AssetRipper export generated nine exact source Texture2DArray/private Unity Editor contract entries and all 28 ClassID187 original Material links, 50 source-pixel layers and two zero-source layers. Its separate optional UnityPy decoder failed with `Texture2D has no image data` while detached original stream bytes were proven in private stage. No Unity Editor import or Adreno claim.
- [43151970478 FAILED](https://github.com/alwansan/raf/actions/runs/43151970478): T5 owner-authorized full native reconstruction authenticated 134/134 ZIP2 source graphics (7,532,909,297 bytes), staged 82/82 pristine owners (819,595,355 bytes), exported real project, then failed at **GT repair nine original array grids** before Unity Editor: `not_all_nine_original_array_targets_found`. No APK/OBB/XAPK artifact or Editor execution.
- Confirmed root cause by comparing production export env with `RaftExportLineage.Capture`: ClassID187 is included only when `RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE=1`; the isolated exporter set it, native exporter did not. This is a missing source→export identity trace, not proof that source PNG/BC3 pixels were damaged.

## Changes pushed and synthetic verification

1. [47b4f3f](https://github.com/alwansan/raf/commit/47b4f3f502189f7b18cd19a8e7cc178fd6dbb13f): repaired production array regression to require *pristine* SHA-verified ZIP2 original owners rather than Mesh-inlined mutable export input. [43152621218 SUCCESS](https://github.com/alwansan/raf/actions/runs/43152621218).
2. [272ab8c1](https://github.com/alwansan/raf/commit/272ab8c1cc9ec8001cc5ca69200daca294978e2f): inject original SHA-authenticated external BC3 stream into UnityPy object reader in-memory only, validate native dimensions/depth/mips/format/data length, never write bytes back. Expanded negative synthetic tests. [43153004857 SUCCESS](https://github.com/alwansan/raf/actions/runs/43153004857).
3. [85316d5](https://github.com/alwansan/raf/commit/85316d5123d593865fbbf4411414bd929b9a6874): added explicit independent UnityPy full-eight-slice layout receipt to GT isolated full workflow; [43153126679](https://github.com/alwansan/raf/actions/runs/43153126679) real 7.53GB source exporter was in progress at this checkpoint.
4. [5f4da8ff](https://github.com/alwansan/raf/commit/5f4da8ffb94659c6c33cfd59fd24d43f25496f91): native AssetRipper env now sets `RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE=1` only inside the production export step. Private JSON stays on runner. Added regression requiring this flag and no `continue-on-error`. [43153342026 SUCCESS](https://github.com/alwansan/raf/actions/runs/43153342026) source-only; **real native retry pending**.

## Remaining proof and handoff

- Read final [43153126679](https://github.com/alwansan/raf/actions/runs/43153126679) independent UnityPy/Pillow decoder step. If it fails, inspect actual typed native vs original stream sizes, never fake data.
- T5 controls future owner-authorized native rerun. Verify private ClassID187 in same-instance export with nine GUIDs; strict nine meta grid correction; 28 original Material pointers; real `OriginalTextureArrayImportGuard` in Unity Editor 2021.3.45f2; and only after all gates, APK/OBB/XAPK.
- Remaining 770 Dummy Shader-backed Materials, 416 external identity links, full 11 mip parity, water/FFT/runtime GPU/device color and gameplay are **not proven fixed** by this GT work.
- No Git LFS, no ZIP2 writes, no broad source .meta rewrites, no unauthorized full XAPK dispatch.
