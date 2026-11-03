# A8 — original ZIP2 SaveAndLoad and .rgd source provider without LFS

**Local date:** 4 November 2026. **Client:** `raft-20261103T224306Z-d17e2cb7` (A8). **Writable branch:** `feature/android-native-port` only. **ZIP2 read-only immutable SHA:** [15964ea8](https://github.com/alwansan/raf/commit/15964ea8f246b6e076ce26b60931ee2e1a9a2385).

## Why this was needed

The existing original SaveAndLoad path-portability workflow checked out `Raft/Raft_Data/Managed` from the development branch. The owner now provides a complete non-LFS original game source on `zip2`. Rather than copying all 7.79GB over the development tree or fetching LFS, this change uses sparse ZIP2 inputs for a bounded original-source validation. A1's independent FFT and A2's Settings work already use ZIP2 for different original data; this task changes only the save-source validation pipeline.

## Concrete changes

- [Source verifier](../scripts/verify_a8_zip2_local_save_provider.py) hard-pins two **plain Git blobs**, validates their unique `RAFT_FILE_MANIFEST.tsv` entries, and rehashes the complete downloaded files before permitting inspection. It rejects wrong-size or same-size modified content, wrong kind/hash/schema, duplicate manifest records, missing source, linked leaves/parent directories, invalid pinned path traversal, invalid independent pins and oversized manifests. It is read-only and does not emit source content.
- [11 synthetic regressions](../tests/test_verify_a8_zip2_local_save_provider.py) include both valid proof and negative controls. Initial run [41733527931](https://github.com/alwansan/raf/actions/runs/41733527931) **FAILED** in one synthetic negative test, exposing a pin path `../escape` that passed the syntax validator; the subsequent source fix [5f5be032](https://github.com/alwansan/raf/commit/5f5be03230b3becc1f9fa88bc86fa9a395919483) rejects `.` and `..` components before any manifest access.
- [Updated no-LFS original save-path CI](../.github/workflows/raft-original-save-path-tests.yml) checks out only scripts/tests from the writable branch, checks out the exact immutable ZIP2 commit by sparse Git fetch, verifies checkout HEAD, original source manifest and SHA/size, then executes **the existing** ILSpy `CSharp9_0` original SaveAndLoad adaptation and Linux path harness against that exact ZIP2 DLL. The source ZIP2 branch is read-only and the generated C# remains runner-private.

## Authenticated original ZIP2 inputs

| Exact original path under `Raft/` | Bytes | SHA256 |
|---|---:|---|
| `Raft_Data/Managed/Assembly-CSharp.dll` | 3,211,776 | `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e` |
| `Raft_Data/StreamingAssets/Data.rgd` | 2,941 | `b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba` |

**Independence:** the above expected size/hash pairs are constants in the test provider, not accepted from the Git manifest alone; the manifest must agree and the actual file contents must independently hash to the same pinned values. The original `Data.rgd` is a StreamingAssets input, **not** evidence of a generated player-world save or an on-device load roundtrip.

## Verified GitHub Actions

- [Final same-source run 41733872815](https://github.com/alwansan/raf/actions/runs/41733872815), job `126257897836`, source `5f5be03230b3becc1f9fa88bc86fa9a395919483`: **COMPLETED SUCCESS**. Verified ZIP2 source checkout, exact 2 originals/3,214,717 bytes/SHA256, 11/11 synthetic tests, 6/6 existing path adapter tests, 4/4 original-source selector tests; private original SaveAndLoad CSharp9 decompilation, 16 original path-expression transformations, original-source fidelity/idempotence, and 14 executable Linux/Windows expression checks all passed. No LFS.
- [Initial RED 41733527931](https://github.com/alwansan/raf/actions/runs/41733527931), source `3e354068cfbd62a684d3f9211d15961f898d4851`: **COMPLETED FAILURE** in one synthetic path pin negative control, before original provider verification; fixed at `5f5be032`. It was not a Unity build failure.

## Limits and next work

This produces no original game source exports, no changed game code, .meta, GUID, .rgd content, shader/colour/material, and no native build, APK/OBB/XAPK, signed release or schedule changes. The original DLL is only inspected/decompiled as data, not run as a Windows game. Existing local RPC/harness and path compatibility outcomes are not original Android save/load runtime evidence; a true offline create/save/load/resume with generated .rgd data and phone evidence remains pending. Likewise WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN, game stays **NOT_READY / 0-of-3 readiness reviews**.

Next independent development: source-authenticate full original create/load/save/resume coupling and test on-device only after genuine native source/render gates are ready. Continue migrating individual original-data consumers to ZIP2 by independent verified pins, not wholesale replacement of existing development Raft tree.
