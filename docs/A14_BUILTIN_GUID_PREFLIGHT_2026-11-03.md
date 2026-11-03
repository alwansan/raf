# A14 — matched original shader .meta GUID preflight (3 November 2026)

**Scope:** RENDER-002, client `raft-20261103T225203Z-a14c07d9`, session `A14-20261103T225203Z-1d3c44b2`. Resumed from completed A14 `raft-20261103T123119Z-9fd895b8`, preserving previous records.

## Source defect and correction

The original built-in shader restoration path only required matched exported `.shader.meta` files to exist and not be symlinks; it did not verify the GUID identity it promised to preserve. This could allow malformed/missing/multiple GUID records or collisions between matched ShaderLab sources to reach external backup and shader replacement.

[Source fix 7252455](https://github.com/alwansan/raf/commit/7252455a8e0b4943bdc13ed3b222c99b34054a90) checks exactly one top-level `guid:` field with 32 hex digits per matched shader and rejects case-insensitive duplicates among **matched exported shaders** before external backup creation or asset mutation. It preserves `.meta` bytes exactly, including original line endings and nested importer data, and never publishes proprietary shader identities.

## Synthetic CPU proof

- [A14 new source CI41735307997](https://github.com/alwansan/raf/actions/runs/41735307997): 9/9 PASS (5 GUID cases +4 backup failure cases).
- Independent peer A9, A15 and vendor tests on the first new source failed because older fixtures used non-hex *synthetic* `guid: original-...` values. [Valid 32-hex fixture correction b7a4daaf](https://github.com/alwansan/raf/commit/b7a4daaf8ce67b844c57d5d205dadac7db41c587), [vendor inline fixture 1b6d754f](https://github.com/alwansan/raf/commit/1b6d754fd2546c9bb35d290b21c26381e61c4c3c), [A3 fixture 94e13924](https://github.com/alwansan/raf/commit/94e139247f82b701ab29f7adbcef7afd050e96d3) replace only test-data identifiers; no peer production logic altered.
- [Final combined A14 CI41736092400](https://github.com/alwansan/raf/actions/runs/41736092400): **SUCCESS** on [source 91a84466](https://github.com/alwansan/raf/commit/91a84466fcf14f980149a931109ec2e2f1e45344), job126265565649. Five suites 9+4+4+4+10 = **31/31 PASS** at same immutable source SHA. All synthetic; no Git LFS, Unity import, native run, APK/OBB/XAPK, Release or original assets.

## Limits and open project gates

This proves only fail-closed preflight behavior on synthetic files. It does not validate all original export GUIDs or cross-asset GUID collisions; no original full ShaderLab export, real render pass, Water FFT kernel, Unity compiler, Vulkan phone execution, GPU water rendering, colours or device logs were tested.

Old native preview [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) still failed its zero built-in shader identity intersection before Unity. RENDER-002, WATER-001 and FFT-FORMAT-009 remain OPEN; readiness **NOT_READY / 0 of 3** full independent identical-source readiness reviews. The next work requires authenticated full original export identity and genuine shader/pass restoration, not relaxation of the existing strict gate.
