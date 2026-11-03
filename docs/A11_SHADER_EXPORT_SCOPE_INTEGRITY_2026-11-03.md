# A11 — read-only shader export scope integrity (3 November 2026)

**Owner:** A11 / `raft-20261103T123040Z-02fe66b3`, RENDER-002. **Status:** bounded diagnostic completed; global RENDER-002 **OPEN**, WATER-001/FFT-FORMAT-009 **OPEN**, game **NOT_READY** and full candidate review **0/3**.

## Verified historical failure and provenance gap

[Native run 41624581951](https://github.com/alwansan/raf/actions/runs/41624581951), source `c7254f7d`, reconstruct job `125878883840` FAILED at step25 before Unity while restoring exact-name official Unity 2021.3.45f2 built-in shaders. The official ZIP passed its SHA-256 guard and provided **198 runtime built-in identities**. The exported-run aggregate emitted `RAFT_EXPORTED_RENDER_CONTRACT shaders=140 source_pass_histogram={1: 140} computes=0`; the subsequent built-in restorer reported **zero exact matches** and failed closed. Older A9/A3/A6 fixes address identity parser, symlink and include correctness, not original complete-export matching. The different local 107-file inventory (24 empty, 83 parseable nonvendor, zero matches) has not been tied to the entire failed export or even its exact pipeline phase. A13 later improved the preexisting 107-sample parser [CI 41637048446](https://github.com/alwansan/raf/actions/runs/41637048446), independently of A11.

## Independent A11 implementation

- [Script d5aa9e4d](https://github.com/alwansan/raf/commit/d5aa9e4d5005b3e90f65b1b7cd26c497cf41dcf4) adds `scripts/probe_a11_shader_export_scope.py`. It creates an **in-situ local** read-only snapshot of exported `.shader` / `.compute` plus associated `.meta` files, using SHA-256 of source bytes, metadata and relative file paths. It detects additions, removals, rename, content or .meta drift; fails on unsafe symlinks, absent metadata and empty inventory. Outputs only aggregate counts/hash identifiers, never raw original names or shader content.
- [Test d e5c65a](https://github.com/alwansan/raf/commit/de5c65a335d883e0005f7ddca46a68e898aaee51) adds 11 isolated synthetic Python regression checks, including intentional 107-vs-140 **same-scope hypothetical** mismatch. Historical sample-to-run scope equality is **not established**, so no conclusion of 33 missing shaders in the real export follows.
- [Isolated workflow d01411409](https://github.com/alwansan/raf/commit/d01411409e1e422c04b78533e65e138613a43573) uses ubuntu-24.04, 8-minute timeout, client-unique concurrency, cancel-in-progress false, no LFS/Unity, and an aggregate-only test log artifact.
- [Exact workflow Actions 41637552496](https://github.com/alwansan/raf/actions/runs/41637552496), job125922462387 **COMPLETED SUCCESS, 11/11 tests**. Independently checked byte-exact Git blob hashes for source `cf4a19301f1787b3039413e9cfaedd25c0afd2a2`, tests `ee692dd67446816dbc33527215dd918c0212dc14`, workflow `d12fd4250ba232444be54a0975dc2b7df23fcffc` matching locally tested files.

## How to use for authorized later analysis

Within the same original AssetRipper-export workspace, capture a local snapshot before any shader replacement:

```sh
python3 -m scripts.probe_a11_shader_export_scope --project "$PROJECT" --write-local-snapshot "$RUNNER_TEMP/shader-scope-private.json"
python3 -m scripts.probe_a11_shader_export_scope --project "$PROJECT" --verify-local-snapshot "$RUNNER_TEMP/shader-scope-private.json" --expected-shaders 140 --expected-computes 0
```

The `140/0` operands above are **historical observations** from run41624581951 and **MUST NOT** be assumed correct for a different source/export run. The snapshot is a **local integrity check**, not authenticated original-export provenance: both success and failure still report `original_export_provenance_verified=false`, `built_in_identity_matches_verified=false` where applicable, `ready_for_build=false`. If expected counts or pipeline phases differ, comparison fails; do not edit the strict water or built-in shader gates merely to pass it. Do not publish the local manifest when it could disclose original-resource identifiers by correlation.

## Boundaries and follow-up

This A11 task intentionally did not modify source shaders, ShaderLab declarations, .meta/GUIDs or original assets; it made no LFS fetch, Unity/native/editor build, APK/OBB/XAPK/release, native request change, CL write or task edit. It **does not recover any original built-in, custom water, FFT or postprocessing program**, validate shader identity matches, or prove Android execution. Next use an authenticated full exported-in-run inventory (same stage/source and counts) and inspect its exact zero-match cause before considering any mapped restoration. Do not reuse the 107 local sample as full-run evidence.

Branch ref update via GitHub `update_ref(expected_sha)` errored at provider level; only exclusive new-path writes and conditional blob-SHA `update_file` calls were used. Owner branch protection and independent clients were preserved.
