# A11 RENDER-002 — fail-closed shader export scope integrity v2 (2026-11-03)

Owner: A11 / `raft-20261103T123040Z-02fe66b3`. Source branch: `feature/android-native-port`. Local source fixes only; **RENDER-002 and WATER-001 remain OPEN, overall game NOT_READY, no candidate and readiness 0/3**.

## Verified defect and RED evidence

The previously completed [A11 v1 tool](A11_SHADER_EXPORT_SCOPE_INTEGRITY_2026-11-03.md) retained a read-only hash snapshot but accepted six safety/provenance blind spots on synthetic examples: a symlinked ancestor of the project directory, malformed `.shader.meta` GUID syntax, duplicate valid GUIDs in two different shader files, orphan shader metadata without corresponding source, ignored expected source counts during `--write-local-snapshot`, and incomplete one-sided expected counts. These are confirmed defects of the audit utility, **not demonstrated defects in the owner's original Raft export**.

Independent synthetic **RED** test-only commit [11336a6c](https://github.com/alwansan/raf/commit/11336a6c94b9f97d56dabe8e0f716dabb7772c71), [GitHub Actions41644180493](https://github.com/alwansan/raf/actions/runs/41644180493), job125945034210: **COMPLETED FAILURE AS EXPECTED**, 6/17 new safety assertions failed on the unchanged production A11 script; the existing 11 tests remained green. No original proprietary shader contents were used.

## Bounded fix and GREEN evidence

[Fix commit9e85d22](https://github.com/alwansan/raf/commit/9e85d22cc195d239048be1ef145ec3626e76fc26) modifies only `scripts/probe_a11_shader_export_scope.py`, with the 17-case tests already installed by the red commit. It rejects symlinked project path components before traversal, parses and checks a single 32-hex Unity GUID for each source metadata and rejects collisions, fails on orphan shader/compute `.meta` leaves, and enforces **paired exact** expected shader/compute counts even at snapshot creation before writing any output. The tool continues hashing relative paths/source/meta and emitting only counts, aggregate hashes and fixed error codes, without printing shader names, original GUIDs, proprietary bytes or source. It performs **read-only** analysis of the original asset tree.

[Exact-source GREEN GitHub Actions41644281473](https://github.com/alwansan/raf/actions/runs/41644281473), job125945393211: **COMPLETED SUCCESS, 17/17 synthetic tests**, with aggregate-only [artifact13234366506](https://github.com/alwansan/raf/actions/runs/41644281473/artifacts/13234366506). Git blob SHA1 for code `12096810a976505d509f95f82960b67b4f22d7e0` and test `f988fb3bfe3f271595c2535a10c733957b53de33` equals independently tested local files. Existing workflow `.github/workflows/raft-a11-shader-export-scope.yml` retained unchanged, 8-minute CPU-only concurrency, no LFS/Unity.

## Limits and next engineering gate

The historical [full native41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) still FAILED **before Unity** at zero authenticated built-in shader identity matches (pre-restoration aggregate had140 shader stubs, 0 compute). The local 107-file subset is **not authenticated as that full export or same stage**. A11 v2 did **not** execute AssetRipper, acquire complete original export, resolve a single real original ShaderLab/vendor identity, restore shaders, run GPU/Unity/APK/OBB/XAPK, alter any original `.meta`/GUID or material, use LFS, touch `alwansan/CL`, protected branches, schedules or native requests.

Future permitted work: obtain an in-run same-stage full-export digest/count and compare authoritative ShaderLab identities, then diagnose the zero-match cause without inventing names or loosening the strict water/builtin gates. A locally valid 17/17 utility is not a proof of complete original shader export, render correctness or readiness for build.
