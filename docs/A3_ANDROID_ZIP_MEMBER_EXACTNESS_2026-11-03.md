# A3 — Exact APK/OBB ZIP entry spelling audit (3 November 2026)

## Verified result

Only `feature/android-native-port` was written. This scoped task fixed a **synthetic-proven defect in the pre-delivery APK+OBB structural validator**, not a game crash or the shader/kernel blockers.

Before the fix, `scripts/audit_android_expansion.py::_names` checked `PurePosixPath(name).parts`. Python normalizes away both an explicit `.` component and repeated `/` separators, even though `zipfile.ZipInfo.filename` and Android jar ZIP entry lookup retain the raw spelling. Therefore the old preflight accepted confusing ZIP filenames such as `assets/bin/Data/./level2` and `assets/bin/Data//level2` (with a separate valid scene entry present), allowing structurally invalid extra content to pass. These are **synthetic counterexamples**, not observed actual APK/OBB members.

- **RED commit [5d7f2e3a](https://github.com/alwansan/raf/commit/5d7f2e3afc5bbd4c48c6a40d3286407e3608d33e)**: [CPU run 41641061681](https://github.com/alwansan/raf/actions/runs/41641061681), job125934396072, **FAILED as expected**, 5 failing of 8 tests (five missing exceptions) for APK and OBB malformed raw names; three controls passed (normal members, legal trailing-slash directories, existing parent-traversal rejection).
- **GREEN source [7faf0a8b](https://github.com/alwansan/raf/commit/7faf0a8bb557e59131a92a062bd2571c98547b8c)**: checks `name.split('/')` segments literally and rejects empty, `.`, `..` components, allowing exactly one trailing empty segment for `ZipInfo.is_dir()` because explicit ZIP directory entries normally end in `/`. Keeps the original path, drive marker, slash/backslash and duplicate checks; never prints real ZIP member names or copies/rewrites payload.
- **GREEN [CPU run 41641182243](https://github.com/alwansan/raf/actions/runs/41641182243)**, job125934812340, **COMPLETED SUCCESS on the exact fix SHA**: all **8/8** new A3 test-owned APK/OBB ZIP fixtures and **13/13** existing expansion and original Haptics contract tests passed.
- Same-source existing lightweight workflows independently passed: [A5 Haptics ZIP contract 41641182249](https://github.com/alwansan/raf/actions/runs/41641182249), [unit preflight 41641182147](https://github.com/alwansan/raf/actions/runs/41641182147), and [offline platform adapter 41641182250](https://github.com/alwansan/raf/actions/runs/41641182250). No LFS, Unity or device build was triggered.

## Changes and scope

Source modified: `scripts/audit_android_expansion.py`. Added `tests/test_a3_zip_entry_paths.py`, `.github/workflows/raft-a3-zip-member-paths.yml` (ubuntu-24.04, 6-minute CPU-only budget, unique group, cancel-in-progress:false). Work and experiment live under `prompt/coordination/clients/raft-20261103T124800Z-a3b9e27f` and per-issue files. Other Haptics audit, the native build workflow, ZIP library, original game resources, metadata, GUIDs, LEFT Mouse0/500ms, FMOD, shader code, `.rgd` and all protected branches were left untouched.

This **does not** authenticate complete original scene bytes, guarantee official Unity output canonicalization, establish an actually mounted OBB, eliminate file races, or demonstrate phone performance. Original WATER-001 / RENDER-002 / FFT-FORMAT-009 are still open, candidate absent, **NOT_READY and immutable full readiness reviews 0/3**. The last game delivery was APK80 from older source; newer code has no device acceptance from this CPU-only experiment. Do not dispatch a game build solely because this check passed.

## Next relevant work

Continue real restoration of original shader/pass/kernel identities, GPU numeric/format comparison and local-world/input acceptance under coordination. When a separate readiness coordinator authorizes actual Unity build after prerequisites, its existing APK/OBB audit automatically enforces this source-level exact path validation without another workflow change.
